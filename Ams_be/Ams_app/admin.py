from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User,Attendance,Holiday,Shift,LeaveRequest


class UserAdmin(BaseUserAdmin):
    list_display = ('email','name','role','is_active','is_staff')
    list_filter = ('role','is_staff','is_active')
    search_fields = ('email','name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email','password')}),
        ('Personal Info', {'fields': ('name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions',)


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


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'leave_type', 'start_date', 'end_date', 'status', 'approved_by', 'applied_at')
    list_filter = ('leave_type', 'status')
    search_fields = ('employee__user__username', 'reason')
    readonly_fields = ('applied_at',)

# Holiday model admin
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date','start_date','end_date', 'description')  # Display these fields in the list view
    search_fields = ('name', 'date')  # Make the name and date fields searchable
    list_filter = ('date', 'end_date')  # Filter by date and last_date

# Shift model admin 
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'is_active')  # Display these fields in the list view
    search_fields = ('name', 'start_time', 'end_time')  # Make the name, start_time, and end_time searchable
    list_filter = ('is_active', 'start_time')  # Filter by active status and start_time

# Register models with the admin site
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(User, UserAdmin)