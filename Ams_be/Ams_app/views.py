# Ams_app/views.py
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse
from rest_framework import generics, permissions, viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
import openpyxl

from .models import Attendance, LeaveRequest, Shift, Holiday, User
from .serializers import (
    AttendanceReportSerializer,
    AttendanceSerializer,
    LeaveRequestSerializer,
    ShiftSerializer,
    HolidaySerializer,
    UserSerializer
)
from .permissions import (
    IsAdminOrHR,
    IsAdminOrSelf,
    IsAdminHRorSelf,
    IsNotHoliday,
)

# User Management Views

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Open registration


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

# Attendance Views

class AttendanceListCreateView(generics.ListCreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Attendance.objects.all() if user.is_staff else Attendance.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]


class AttendanceReportView(generics.ListAPIView):
    serializer_class = AttendanceReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]

    def get_queryset(self):
        employee_id = self.request.query_params.get('employee_id')
        if not employee_id:
            raise PermissionDenied("Please provide an employee_id in query params.")
        last_30_days = timezone.now().date() - timedelta(days=30)
        return Attendance.objects.filter(user__id=employee_id, date__gte=last_30_days)


class AttendanceReportExcelView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]

    def get(self, request, *args, **kwargs):
        employee_id = request.query_params.get('employee_id')
        if not employee_id:
            raise PermissionDenied("Please provide an employee_id in query params.")

        last_30_days = timezone.now().date() - timedelta(days=30)
        records = Attendance.objects.filter(user__id=employee_id, date__gte=last_30_days)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Attendance Report"
        ws.append(["Date", "Check-In", "Check-Out", "Status"])

        for record in records:
            ws.append([
                record.date.strftime("%Y-%m-%d"),
                record.check_in.strftime("%H:%M:%S") if record.check_in else "",
                record.check_out.strftime("%H:%M:%S") if record.check_out else "",
                record.status
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=attendance_report_user_{employee_id}.xlsx'
        wb.save(response)
        return response

# Leave Request Views

class LeaveRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return LeaveRequest.objects.all() if user.role in ['Admin', 'HR'] else LeaveRequest.objects.filter(employee=user)

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)


class LeaveRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminHRorSelf]


class LeaveApprovalView(generics.UpdateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        leave = self.get_object()
        if request.user.role != 'HR':
            return Response({'detail': 'Only HR can approve/reject leaves.'}, status=status.HTTP_403_FORBIDDEN)

        status_value = request.data.get('status')
        if status_value not in ['Approved', 'Rejected']:
            return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        leave.status = status_value
        leave.approved_by = request.user
        leave.save()
        return Response({'detail': f'Leave {status_value.lower()}.'})

# Shift & Holiday Views

class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsNotHoliday]


class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
