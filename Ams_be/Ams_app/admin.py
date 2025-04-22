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
