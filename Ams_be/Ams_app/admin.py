from django.contrib import admin

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
