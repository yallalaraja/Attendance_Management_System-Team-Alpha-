from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Attendance, Holiday, Shift, LeaveRequest, UserShiftAssignment

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'role', 'is_active','is_staff')  # Removed 'is_staff' from list_display
    list_filter = ('role', 'is_active')  # Removed 'is_staff' from list_filter
    search_fields = ('email', 'name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'role', 'shift')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),  # Removed 'is_staff'
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'shift', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'status', 'check_in', 'check_out','get_total_hours')
    list_display_links = ('user',)
    list_filter = ('status', 'date')
    search_fields = ('user__email', 'user__name', 'date')
    ordering = ('-date',)

    def get_readonly_fields(self,request,obj=None):
        if obj:
            return self.readonly_fields + ('user', 'date', 'check_in', 'check_out', 'status')
        return self.readonly_fields


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'leave_type', 'start_date', 'end_date', 'status', 'approved_by', 'applied_at')
    list_display_links = ('id',)
    list_filter = ('leave_type', 'status')
    search_fields = ('employee__email', 'employee__name', 'reason')
    readonly_fields = ('applied_at',)

    def save_model(self, request, obj, form, change):
        if obj.status == 'Approved' and not obj.approved_by:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'description')
    search_fields = ('name', 'start_date')
    list_filter = ('start_date', 'end_date')
    ordering = ('start_date',)


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active', 'start_time')


@admin.register(UserShiftAssignment)
class UserShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'shift', 'date')
    list_filter = ('shift', 'date')
    search_fields = ('user__email', 'user__name', 'shift__name')
