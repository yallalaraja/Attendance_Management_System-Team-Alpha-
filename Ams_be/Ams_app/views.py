from datetime import date, timedelta
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework.response import Response
from django.utils.timezone import now
from .models import Attendance, User, LeaveRequest, Shift, UserShiftAssignment, Holiday
from .serializers import (
    AttendanceSerializer, LeaveRequestSerializer, ShiftSerializer,
    UserShiftAssignmentSerializer, UserSerializer, HolidaySerializer
)
from .permissions import IsAdminOrHR


# ----- User View ----- #
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'HR']:
            return User.objects.all()
        return User.objects.filter(id=user.id)


# ----- Attendance Views (Employee only) ----- #
class AttendanceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        employee = request.user
        end_date = now().date()
        start_date = end_date - timedelta(days=30)
        attendance_data = Attendance.objects.filter(user=employee, date__range=(start_date, end_date))
        serializer = AttendanceSerializer(attendance_data, many=True)
        return Response(serializer.data)

    def create(self, request):
        employee = request.user
        current_time = now().time()
        today = date.today()

        try:
            attendance = Attendance.objects.get(user=employee, date=today)
            if attendance.check_in and not attendance.check_out:
                attendance.check_out = current_time
                attendance.status = 'Checked-Out'
            else:
                return Response({"error": "Attendance already recorded for today"}, status=400)
        except Attendance.DoesNotExist:
            attendance = Attendance(user=employee, date=today, check_in=current_time, status='Checked-In')

        attendance.mark_check_in()
        attendance.save()
        return Response({"message": "Attendance recorded successfully"}, status=201)


# ----- Attendance Report Views (Admin/HR only) ----- #
class AttendanceReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrHR]

    def list(self, request, user_id=None):  # Add user_id as a URL parameter
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        try:
            employee = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        end_date = now().date()
        start_date = end_date - timedelta(days=30)
        attendance_data = Attendance.objects.filter(user=employee, date__range=(start_date, end_date))
        serializer = AttendanceSerializer(attendance_data, many=True)
        return Response(serializer.data)

# ----- Leave Request Views (All users, access limited) ----- #
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'HR']:
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.filter(employee=user)

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.role in ['Admin', 'HR'] and self.request.data.get('status') == 'Approved':
            serializer.save(approved_by=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrHR])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'Approved'
        leave.approved_by = request.user
        leave.save()

        serializer = self.get_serializer(leave)
        return Response(serializer.data, status=200)


# ----- Shift Views (Admin/HR only) ----- #
class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]

    def get_queryset(self):
        return Shift.objects.all()


# ----- User Shift Assignment Views (Admin/HR only) ----- #
class UserShiftAssignmentViewSet(viewsets.ModelViewSet):
    queryset = UserShiftAssignment.objects.all()
    serializer_class = UserShiftAssignmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]

    def get_queryset(self):
        return UserShiftAssignment.objects.all()


# ----- Holiday Views (Admin/HR only) ----- #
class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]

    def perform_create(self, serializer):
        today = date.today()
        # Check if today is within any holiday range
        holiday = Holiday.objects.filter(start_date__lte=today, end_date__gte=today).first()

        if holiday:
            raise serializers.ValidationError(
                f"Today is a holiday ({holiday.name}) from {holiday.start_date} to {holiday.end_date}. Your presence will not be added."
            )

        serializer.save(employee=self.request.user)

    def get_queryset(self):
        return Holiday.objects.all()













from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
from .models import Attendance, LeaveRequest, Shift, UserShiftAssignment, Holiday
from .forms import LeaveRequestForm  # We’ll create this next

# Utility role checks
def is_admin_or_hr(user):
    return user.role in ['Admin', 'HR']

# ----- Attendance Views ----- #

@login_required
def attendance_check(request):
    today = date.today()
    employee = request.user
    current_time = now().time()
    attendance = Attendance.objects.filter(user=employee, date=today).first()

    if request.method == 'POST':
        if attendance:
            if not attendance.check_out:
                attendance.check_out = current_time
                attendance.status = 'Checked-Out'
                attendance.save()
        else:
            # Create a new attendance record
            attendance = Attendance(user=employee, date=today, check_in=current_time, status='Checked-In')
            attendance.save()

    return render(request, 'ams_app/attendance/attendance_check.html', {'attendance': attendance})

@login_required
def attendance_history(request):
    employee = request.user
    end_date = now().date()
    start_date = end_date - timedelta(days=30)  # Get attendance data for the last 30 days
    attendance_data = Attendance.objects.filter(user=employee, date__range=(start_date, end_date))

    return render(request, 'ams_app/attendance/history.html', {'attendance_data': attendance_data})

# ----- Leave Request Views ----- #

@login_required
def leave_request_form(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user  # Assign the current user as the employee for the leave request
            leave.save()  # Save the form instance
            return redirect('leave_list')  # Redirect to the leave list view after success
    else:
        form = LeaveRequestForm()  # Instantiate an empty form

    return render(request, 'ams_app/leave/apply_leave.html', {'form': form})

@login_required
def leave_list(request):
    user = request.user
    if user.role in ['Admin', 'HR']:
        leaves = LeaveRequest.objects.all()  # Admin/HR sees all leave requests
    else:
        leaves = LeaveRequest.objects.filter(employee=user)  # Employees only see their own leave requests

    return render(request, 'ams_app/leave/leave_list.html', {'leaves': leaves})

# ----- Shift Views ----- #

@login_required
@user_passes_test(is_admin_or_hr)
def shift_list(request):
    shifts = Shift.objects.all()  # Display all shifts for Admin/HR
    return render(request, 'ams_app/shift/shift_list.html', {'shifts': shifts})

# ----- Holiday Views ----- #

@login_required
def holiday_list(request):
    holidays = Holiday.objects.all()  # Show all holidays to the user
    return render(request, 'ams_app/holiday/holiday_list.html', {'holidays': holidays})

# ----- Attendance Report (Admin/HR only) ----- #

@login_required
@user_passes_test(is_admin_or_hr)
def attendance_report(request, user_id=None):
    if not user_id:
        return redirect('error_view')  # You can redirect to an error page or show a message

    try:
        employee = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('error_view')  # You can show an error page or message here

    end_date = now().date()
    start_date = end_date - timedelta(days=30)
    attendance_data = Attendance.objects.filter(user=employee, date__range=(start_date, end_date))

    return render(request, 'ams_app/attendance/attendance_report.html', {'attendance_data': attendance_data, 'employee': employee})

def all_attendance_today(request):
    today = now().date()
    attendance_records = Attendance.objects.filter(date=today).select_related('user')
    return render(request, 'ams_app/attendance/all_attendance.html', {
        'attendance_records': attendance_records,
        'today': today
    })

def all_attendance_last_30_days(request):
    from_date = now().date() - timedelta(days=30)
    attendance_records = Attendance.objects.filter(date__gte=from_date).select_related('user').order_by('-date')
    return render(request, 'ams_app/attendance/all_attendance.html', {
        'attendance_records': attendance_records
    })
