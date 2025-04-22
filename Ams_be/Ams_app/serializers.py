# Ams_app/serializers.py
from rest_framework import serializers
from .models import Attendance

class AttendanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['date', 'check_in', 'check_out', 'status']
