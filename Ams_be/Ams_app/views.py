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
