# admin.py
from django.contrib import admin
from .models import Holiday, Shift

# Register your Holiday model
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'last_date', 'description')  # Display these fields in the list view
    search_fields = ('name', 'date')  # Make the name and date fields searchable
    list_filter = ('date', 'last_date')  # Filter by date and last_date

# Register your Shift model
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'is_active')  # Display these fields in the list view
    search_fields = ('name', 'start_time', 'end_time')  # Make the name, start_time, and end_time searchable
    list_filter = ('is_active', 'start_time')  # Filter by active status and start_time

# Register models with the admin site
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(Shift, ShiftAdmin)
