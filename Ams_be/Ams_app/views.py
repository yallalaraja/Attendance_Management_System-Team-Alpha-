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

# user views for template
from django.shortcuts import render, redirect
from .models import User, Shift
from django.contrib.auth import login, authenticate
from django.contrib import messages

def create_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        name = request.POST['name']
        role = request.POST['role']
        password = request.POST['password']
        shift_id = request.POST.get('shift')

        shift = Shift.objects.get(id=shift_id) if shift_id else None

        user = User.objects.create_user(email=email, name=name, role=role, password=password, shift=shift)
        messages.success(request, f'User {user.name} created successfully!')

        return redirect('login')  # Redirect to login page after successful registration
    
    shifts = Shift.objects.all()
    return render(request, 'ams_app/user/create_user.html', {'shifts': shifts})



from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page after successful login
        else:
            messages.error(request, 'Invalid login credentials. Please try again.')

    return render(request, 'ams_app/user/login.html')

@login_required
def home_view(request):
    return render(request, 'ams_app/home.html')

# logout functionality
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

@require_POST
def logout_user(request):
    logout(request)
    return redirect('login')  # Replace 'login' with your actual login view name

# ----- Attendance Views for templates ----- #

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import timedelta
from Ams_app.models import Attendance

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from .models import Attendance


@login_required
def attendance_status(request):
    user = request.user
    today = date.today()

    try:
        attendance_record = Attendance.objects.get(user=user, date=today)
        checkin_time = attendance_record.checkin_time
        checkout_time = attendance_record.checkout_time

        if checkin_time and checkout_time:
            checkin_datetime = datetime.combine(today, checkin_time)
            checkout_datetime = datetime.combine(today, checkout_time)
            duration = checkout_datetime - checkin_datetime

            # Format duration to hours and minutes
            total_seconds = duration.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            duration_str = f"{hours}h {minutes}m"
        else:
            duration_str = "Not completed"
    except Attendance.DoesNotExist:
        checkin_time = None
        checkout_time = None
        duration_str = "No record"

    context = {
        'user': user,
        'checkin_time': checkin_time,
        'checkout_time': checkout_time,
        'duration': duration_str,
    }

    return render(request, 'ams_app/attendance/status.html', context)


# ----- Leave Request Views for templates ----- #

from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from .models import LeaveRequest

User = get_user_model()

def apply_leave(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        user = User.objects.get(id=user_id)

        LeaveRequest.objects.create(
            user=user,
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            leave_type=request.POST.get('leave_type'),
            reason=request.POST.get('reason')
        )
        return redirect('leave_success')  # or wherever you want to redirect

    context = {}
    if request.user.is_superuser or request.user.role in ["Admin", "HR"]:
        context['users'] = User.objects.all()
    return render(request, 'ams_app/leave/apply_leave.html', context)

@login_required
def leave_list(request):
    user = request.user
    if user.role in ['Admin', 'HR']:
        leaves = LeaveRequest.objects.all()  # Admin/HR sees all leave requests
    else:
        leaves = LeaveRequest.objects.filter(employee=user)  # Employees only see their own leave requests

    return render(request, 'ams_app/leave/leave_list.html', {'leaves': leaves})

# ----- Shift Views for templates ----- #

@login_required
@user_passes_test(is_admin_or_hr)
def shift_list(request):
    shifts = Shift.objects.all()  # Display all shifts for Admin/HR
    return render(request, 'ams_app/shift/shift_list.html', {'shifts': shifts})

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .models import Shift, UserShiftAssignment

User = get_user_model()

from datetime import date

from django.contrib import messages

def allocate_shift(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        shift_id = request.POST.get('shift_id')

        user = User.objects.get(id=user_id)
        shift = Shift.objects.get(id=shift_id)

        today = date.today()  # Set today's date or any other logic

        # Create or update shift allocation
        UserShiftAssignment.objects.update_or_create(
            user=user,
            date=today,
            defaults={'shift': shift}
        )

        messages.success(request, f"Shift '{shift.name}' allocated to {user.name} successfully!")

        return redirect('shift_allocate')  # Use the correct URL name

    context = {
        'users': User.objects.all(),
        'shifts': Shift.objects.all(),
        'assignments': UserShiftAssignment.objects.select_related('user', 'shift'),
    }
    return render(request, 'ams_app/shift/allocate_shift.html', context)


# ----- Holiday Views for templates ----- #

@login_required
def holiday_list(request):
    holidays = Holiday.objects.all()  # Show all holidays to the user
    return render(request, 'ams_app/holiday/holiday_list.html', {'holidays': holidays})

# Add Holiday
def add_holiday(request):
    if request.method == "POST":
        holiday_name = request.POST.get('holiday_name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')

        if holiday_name and start_date and end_date and description:
            try:
                # Create the Holiday object correctly
                holiday = Holiday.objects.create(
                    name=holiday_name,
                    start_date=start_date,
                    end_date=end_date,
                    description=description
                )
                messages.success(request, "Holiday added successfully!")
            except Exception as e:
                messages.error(request, f"Error: {e}")
                return redirect('add_holiday')

            return redirect('holiday_list')  # Redirect to the holiday list page
        else:
            messages.error(request, "All fields are required.")
            return redirect('add_holiday')

    return render(request, 'ams_app/holiday/add_holiday.html')
