from datetime import datetime, date, timedelta
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now
from .models import Attendance, User, LeaveRequest, Shift, UserShiftAssignment,Holiday
from .serializers import AttendanceSerializer, LeaveRequestSerializer, ShiftSerializer, UserShiftAssignmentSerializer,UserSerializer,HolidaySerializer
from .permissions import IsAdminOrHR,IsWithinAssignedShiftTime,IsEmployee,IsAdminUserForList

class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    Accessible by Admin or HR.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]

    def perform_update(self, serializer):
        # You can customize what happens when a user is updated (e.g., logging or special handling)
        serializer.save()

# ----- Attendance Views ----- #

class AttendanceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsEmployee]

    def list(self, request):
        """
        List all attendance records for the authenticated employee.
        """
        employee = request.user
        end_date = now().date()
        start_date = end_date - timedelta(days=30)

        attendance_data = Attendance.objects.filter(user=employee, date__range=(start_date, end_date))
        serializer = AttendanceSerializer(attendance_data, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Check-in or check-out for the authenticated employee.
        """
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

        attendance.save()
        return Response({"message": "Attendance recorded successfully"}, status=201)


# ----- Attendance Report Views ----- #

class AttendanceReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrHR]

    def list(self, request):
        """
        Get attendance report for a specific employee (Admin or HR only).
        """
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"error": "user_id query parameter is required"}, status=400)

        try:
            employee = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        end_date = now().date()
        start_date = end_date - timedelta(days=30)

        attendance_data = Attendance.objects.filter(user=employee, date__range=(start_date, end_date))
        serializer = AttendanceSerializer(attendance_data, many=True)
        return Response(serializer.data)


# ----- Leave Request Views ----- #

# class LeaveRequestViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = LeaveRequest.objects.all()
#     serializer_class = LeaveRequestSerializer

#     def perform_create(self, serializer):
#         serializer.save(employee=self.request.user)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUserForList]  # Custom permission for 'list' action
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer

    def perform_create(self, serializer):
        # Save the leave request with the logged-in user as the employee
        serializer.save(employee=self.request.user)

    def get_queryset(self):
        """
        Optionally restricts the returned leave requests to the current user.
        """
        queryset = LeaveRequest.objects.all()
        if self.request.user.is_authenticated:
            # Restrict to the logged-in user's leave requests unless the user is admin
            if not self.request.user.is_staff:
                queryset = queryset.filter(employee=self.request.user)
        return queryset

    def perform_update(self, serializer):
        # Set the 'approved_by' field when the leave request is approved
        if self.request.user.is_staff and 'status' in self.request.data and self.request.data['status'] == 'Approved':
            serializer.save(approved_by=self.request.user)  # Set the 'approved_by' field to the HR user
        else:
            super().perform_update(serializer)


class LeaveRequestAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrHR]
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer


# ----- Shift Views ----- #

class ShiftViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrHR]
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer


# ----- User Shift Assignment Views ----- #

class UserShiftAssignmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrHR]
    queryset = UserShiftAssignment.objects.all()
    serializer_class = UserShiftAssignmentSerializer


# ----- Special Condition Views ----- #

class ShiftAssignmentCheckViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsWithinAssignedShiftTime]

    def list(self, request):
        """
        Check if the current time is within the assigned shift for the authenticated user.
        """
        if not request.user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=401)

        now_time = datetime.now().time()
        today = date.today()

        try:
            shift_assignment = UserShiftAssignment.objects.get(user=request.user, date=today)
            shift = shift_assignment.shift
            if shift.start_time <= now_time <= shift.end_time:
                return Response({"message": "Within assigned shift time"}, status=200)
            else:
                return Response({"error": "Not within assigned shift time"}, status=403)
        except UserShiftAssignment.DoesNotExist:
            return Response({"error": "No shift assigned today"}, status=404)
        
class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]
