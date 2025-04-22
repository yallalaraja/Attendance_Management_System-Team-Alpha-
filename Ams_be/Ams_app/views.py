
# Ams_app/views.py
from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Attendance
from .serializers import AttendanceReportSerializer
from .permissions import IsAdminOrManager

class AttendanceReportView(generics.ListAPIView):
    serializer_class = AttendanceReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManager]

    def get_queryset(self):
        employee_id = self.request.query_params.get('employee_id')
        if not employee_id:
            raise PermissionDenied("Please provide an employee_id in query params.")

        last_30_days = timezone.now().date() - timedelta(days=30)
        return Attendance.objects.filter(user__id=employee_id, date__gte=last_30_days)
