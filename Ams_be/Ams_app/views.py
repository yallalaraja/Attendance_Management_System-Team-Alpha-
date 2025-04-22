# Ams_app/views.py
from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions,viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Attendance,LeaveRequest,Shift,Holiday
from .serializers import AttendanceReportSerializer,AttendanceSerializer,LeaveRequestSerializer,ShiftSerializer,HolidaySerializer
from .permissions import IsAdminOrManager,IsAdminOrSelf,IsAdminOrManagerOrSelf,IsNotHoliday

class AttendanceReportView(generics.ListAPIView):
    serializer_class = AttendanceReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManager]

    def get_queryset(self):
        employee_id = self.request.query_params.get('employee_id')
        if not employee_id:
            raise PermissionDenied("Please provide an employee_id in query params.")

        last_30_days = timezone.now().date() - timedelta(days=30)
        return Attendance.objects.filter(user__id=employee_id, date__gte=last_30_days)
    
class AttendanceListCreateView(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Attendance.objects.all()
        return Attendance.objects.filter(user=user)

class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]


class LeaveRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Admin' or user.role == 'HR':
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.filter(employee=user)

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

class LeaveRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManagerOrSelf]

class LeaveApprovalView(generics.UpdateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        leave = self.get_object()

        if request.user.role != 'HR':
            return Response({'detail': 'Only hr can approve/reject leaves.'}, status=status.HTTP_403_FORBIDDEN)

        status_value = request.data.get('status')
        if status_value not in ['Approved', 'Rejected']:
            return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        leave.status = status_value
        leave.approved_by = request.user
        leave.save()
        return Response({'detail': f'Leave {status_value.lower()}.'})
    


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsNotHoliday]


class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer

# employee_management_app/views.py

from rest_framework import generics, permissions
from .models import User
from .serializers import UserSerializer

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Allow open registration

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]