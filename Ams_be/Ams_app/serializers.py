# Ams_app/serializers.py

from rest_framework import serializers
from .models import Attendance, Shift, Holiday, LeaveRequest, User, UserShiftAssignment


# ---------- Attendance Serializers ----------

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['user']


class AttendanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['date', 'check_in', 'check_out', 'status']


# ---------- Leave Request Serializer ----------

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'leave_type', 'start_date', 'end_date',
            'reason', 'status', 'applied_at', 'employee', 'approved_by'
        ]
        read_only_fields = ['id', 'applied_at', 'status', 'employee', 'approved_by']


class LeaveRequestApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['status']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if validated_data.get('status') == 'Approved':
            if instance.employee == request.user:
                raise serializers.ValidationError("Employees can't approve their own leave.")
            instance.approved_by = request.user
        return super().update(instance, validated_data)

# ---------- Shift Serializer ----------

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'


# ---------- User Serializer ----------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ---------- User Shift Assignment Serializer ----------

class UserShiftAssignmentSerializer(serializers.ModelSerializer):
    shift = ShiftSerializer(read_only=True)
    shift_id = serializers.PrimaryKeyRelatedField(queryset=Shift.objects.all(), source='shift', write_only=True)

    class Meta:
        model = UserShiftAssignment
        fields = ['id', 'user', 'date', 'shift', 'shift_id']
        read_only_fields = ['user']

# ---------- Holiday Serializer ----------

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'