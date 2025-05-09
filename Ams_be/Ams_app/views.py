#  ----------------- views created for the backend DRF part ---------------------
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
from .permissions import IsAdminOrManager


# ----- User View ----- #
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'Manager']:
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


# ----- Attendance Report Views (Admin/Manager only) ----- #
class AttendanceReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def list(self, request):
        return Response({
            "detail": "Please use /attendances-report/<user_id>/ to retrieve the past 30 days attendance report for a user."
        })

    def retrieve(self, request, pk=None):  # pk is user_id
        try:
            employee = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        end_date = now().date()
        start_date = end_date - timedelta(days=30)

        attendance_data = Attendance.objects.filter(user=employee, date__range=(start_date, end_date))
        serializer = AttendanceSerializer(attendance_data, many=True)
        return Response(serializer.data)


# ----- Leave Request Views (All users access limited) ----- #
from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework import status

class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['Admin', 'Manager']:
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.filter(employee=user)

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.role in ['Admin', 'Manager'] and self.request.data.get('status') == 'Approved':
            serializer.save(approved_by=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrManager])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'Approved'
        leave.approved_by = request.user
        leave.save()

        serializer = self.get_serializer(leave)
        return Response(serializer.data, status=200)


# ----- Shift Views (Admin/Manager only) ----- #
class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def get_queryset(self):
        return Shift.objects.all()


# ----- User Shift Assignment Views (Admin/Manager only) ----- #
class UserShiftAssignmentViewSet(viewsets.ModelViewSet):
    queryset = UserShiftAssignment.objects.all()
    serializer_class = UserShiftAssignmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def get_queryset(self):
        return UserShiftAssignment.objects.all()


# ----- Holiday Views (Admin/Manager only) ----- #
class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def perform_create(self, serializer):
        start = serializer.validated_data['start_date']
        end = serializer.validated_data['end_date']

        if Holiday.objects.filter(start_date__lte=end, end_date__gte=start).exists():
            raise serializers.ValidationError("Holiday overlaps with an existing one.")

        serializer.save()


    def get_queryset(self):
        return Holiday.objects.all()






#  ----------------- views that we use for the frontend templates --------------

from datetime import datetime
from datetime import date, timedelta
from django.contrib.auth import login,authenticate,logout,get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from .models import Attendance, LeaveRequest, Shift, UserShiftAssignment, Holiday,User, Shift
from django.shortcuts import render, redirect


# Utility role checks
# def is_admin_or_Manager(user):
#     return user.role in ['Admin', 'Manager']

# user views for template
def create_user(request):
    if request.user.role not in ['Admin','Manager']:
        raise PermissionDenied
    
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
    return render(request, 'ams_app/user/create_user.html', {'shifts': shifts,'hide_nav':True})


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

    return render(request, 'ams_app/user/login.html',{'hide_nav':True})

@login_required
def home_view(request):
    return render(request, 'ams_app/home.html')

# logout functionality
@require_POST
def logout_user(request):
    logout(request)
    return redirect('login') 

# ----- Attendance Views for templates ----- #
@login_required
def attendance_check(request):
    user = request.user
    today = date.today()

    # Try to get today’s attendance record
    attendance, created = Attendance.objects.get_or_create(user=user, date=today)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'checkin' and not attendance.check_in:
            attendance.check_in = datetime.now().time()
            attendance.status = 'Present'
            attendance.save()
        elif action == 'checkout' and not attendance.check_out:
            attendance.check_out = datetime.now().time()
            attendance.save()

    checkin_time = attendance.check_in
    checkout_time = attendance.check_out

    # Calculate duration only if both checkin and checkout are available
    if checkin_time and checkout_time:
        checkin_datetime = datetime.combine(today, checkin_time)
        checkout_datetime = datetime.combine(today, checkout_time)
        duration = checkout_datetime - checkin_datetime
    else:
        duration = None

    context = {
        'user': user,
        'checkin_time': checkin_time,
        'checkout_time': checkout_time,
        'duration': duration,
        'status': attendance.status,
    }

    return render(request, 'ams_app/attendance/attendance_check.html', context)


@login_required
def attendance_status(request):
    user = request.user
    today = date.today()

    try:
        attendance_record = Attendance.objects.get(user=user, date=today)
        checkin_time = attendance_record.check_in
        checkout_time = attendance_record.check_out

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

@login_required
def attendance_list(request):
    if request.user.role not in ['Admin', 'Manager']:
        raise PermissionDenied

    attendance_records = Attendance.objects.select_related('user').order_by('-date')

    # Add duration manually to each record
    records_with_duration = []
    for record in attendance_records:
        duration = None
        if record.check_in and record.check_out:
            checkin_dt = datetime.combine(record.date, record.check_in)
            checkout_dt = datetime.combine(record.date, record.check_out)
            duration = checkout_dt - checkin_dt
        records_with_duration.append({
            'record': record,
            'duration': duration,
        })

    context = {
        'attendance_records': records_with_duration
    }
    return render(request, 'ams_app/attendance/attendance_list.html', context)

# ----- Leave Request Views for templates ----- #
def apply_leave(request):
    if request.method == "POST":
        # Get the user ID and fetch the user object
        user_id = request.POST.get('user_id')
        user = User.objects.get(id=user_id)
        
        # Get the start and end date from the form data
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Convert the date strings to datetime objects
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect('apply_leave')  # or the relevant URL
        
        # Validate that the end date is not before the start date
        if end_date < start_date:
            messages.error(request, "End date cannot be before the start date.")
            return redirect('apply_leave')

        # Create the leave request if validation passes
        LeaveRequest.objects.create(
            employee=user,
            start_date=start_date,
            end_date=end_date,
            leave_type=request.POST.get('leave_type'),
            reason=request.POST.get('reason')
        )
        messages.success(request, "Leave request has been submitted successfully.")
        return redirect('leave_list')  # Redirect to the leave list or wherever you want

    context = {}
    if request.user.is_superuser or request.user.role in ["Admin", "Manager"]:
        context['users'] = User.objects.all()
    
    return render(request, 'ams_app/leave/apply_leave.html', context)


def approve_leave(request, leave_id):
    leave_request = LeaveRequest.objects.get(id=leave_id)
    
    # Check if the current user is an Admin or Manager, and not the employee
    if request.user == leave_request.employee:
        messages.error(request, "You cannot approve your own leave request.")
        return redirect('leave_list')  # or wherever you want to redirect
    
    if request.user.role in ["Admin", "Manager"] or request.user.is_superuser:
        leave_request.status = 'Approved'
        leave_request.save()
        messages.success(request, "Leave request approved successfully.")
    else:
        messages.error(request, "You are not authorized to approve this leave request.")
    
    return redirect('leave_list')  # Redirect back to the leave list

def reject_leave(request, leave_id):
    leave_request = LeaveRequest.objects.get(id=leave_id)
    
    # Check if the current user is an Admin or Manager, and not the employee
    if request.user == leave_request.employee:
        messages.error(request, "You cannot reject your own leave request.")
        return redirect('leave_list')  # or wherever you want to redirect
    
    if request.user.role in ["Admin", "Manager"] or request.user.is_superuser:
        leave_request.status = 'Rejected'
        leave_request.save()
        messages.success(request, "Leave request rejected successfully.")
    else:
        messages.error(request, "You are not authorized to reject this leave request.")
    
    return redirect('leave_list')  # Redirect back to the leave list


@login_required
def leave_list(request):
    user = request.user
    if user.role in ['Admin', 'Manager']:
        leaves = LeaveRequest.objects.all()  # Admin/Manager sees all leave requests
    else:
        leaves = LeaveRequest.objects.filter(employee=user)  # Employees only see their own leave requests

    return render(request, 'ams_app/leave/leave_list.html', {'leave_requests': leaves})  # Context updated to match template variable name


# ----- Shift Views for templates ----- #

# View to render the add shift form and process the data
def add_shift(request):
    if request.user.role not in ['Admin','Manager']:
        raise PermissionDenied
    
    if request.method == 'POST':
        # Get form data
        shift_name = request.POST['shift_name']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        
        # Create new shift record
        new_shift = Shift.objects.create(
            name=shift_name,
            start_time=start_time,
            end_time=end_time
        )
        new_shift.save()

        # Redirect to the shift list view after successful creation
        return redirect('shift_list')  # Adjust 'shift_list' to the appropriate URL name
    
    return render(request, 'ams_app/shift/add_shift.html')

@login_required
# @user_passes_test(is_admin_or_Manager)
def shift_list(request):
    if request.user.role not in ['Admin', 'Manager']:
        raise PermissionDenied
    shifts = Shift.objects.all()  # Display all shifts for Admin/Manager
    return render(request, 'ams_app/shift/shift_list.html', {'shifts': shifts})

User = get_user_model()

def allocate_shift(request):
    today = date.today()  # Set today's date or any other logic

    # If Employee, only show their allocation — no shift assignment access
    if request.user.role == "Employee":
        assignment = UserShiftAssignment.objects.filter(user=request.user, date=today).select_related('shift').first()
        context = {
            'employee_shift': assignment,
        }
        return render(request, 'ams_app/shift/employee_shift.html', context)
    
    # For admin/Manager
    if request.user.role not in ['Admin','Manager']:
        raise PermissionDenied
    
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        shift_id = request.POST.get('shift_id')

        user = User.objects.get(id=user_id)
        shift = Shift.objects.get(id=shift_id)

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
    if request.user.role not in ['Admin','Manager']:
        raise PermissionDenied
    
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


# error handling for non admin users
from django.shortcuts import render

def custom_permission_denied_view(request, exception=None):
    return render(request, 'ams_app/errors/403.html', status=403)

