# admin.py
from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'status', 'check_in', 'check_out')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'user__email', 'date')
    ordering = ('-date',)
    readonly_fields = ('user', 'date')

    # Optional: This will prevent editing of user/date after creation from the admin
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('check_in', 'check_out', 'status')
        return self.readonly_fields

from .models import Holiday, Shift
from django.contrib import admin
from .models import Employee, LeaveRequest

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'manager')
    list_filter = ('role',)
    search_fields = ('user__username', 'role')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'leave_type', 'start_date', 'end_date', 'status', 'approved_by', 'applied_at')
    list_filter = ('leave_type', 'status')
    search_fields = ('employee__user__username', 'reason')
    readonly_fields = ('applied_at',)
