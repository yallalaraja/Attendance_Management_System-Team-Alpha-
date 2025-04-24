from django import forms
from .models import Attendance, LeaveRequest, Shift, Holiday
from django.core.exceptions import ValidationError
from datetime import date

# Form for Attendance
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['check_in', 'check_out', 'status']

    def clean_check_in(self):
        check_in = self.cleaned_data.get('check_in')
        if check_in > date.today():
            raise ValidationError("Check-in time cannot be in the future.")
        return check_in

    def clean_check_out(self):
        check_out = self.cleaned_data.get('check_out')
        check_in = self.cleaned_data.get('check_in')

        if check_out and check_out < check_in:
            raise ValidationError("Check-out time cannot be earlier than check-in.")
        return check_out

# Form for Leave Request
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date < date.today():
            raise ValidationError("Leave start date cannot be in the past.")
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')

        if end_date < start_date:
            raise ValidationError("End date cannot be earlier than start date.")
        return end_date

# Form for Shift
class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['name', 'start_time', 'end_time']

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        if start_time < date.today():
            raise ValidationError("Start time cannot be in the past.")
        return start_time

    def clean_end_time(self):
        end_time = self.cleaned_data.get('end_time')
        start_time = self.cleaned_data.get('start_time')

        if end_time <= start_time:
            raise ValidationError("End time must be later than start time.")
        return end_time

# Form for Holiday
class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['name', 'start_date', 'end_date']

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date < date.today():
            raise ValidationError("Holiday start date cannot be in the past.")
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')

        if end_date < start_date:
            raise ValidationError("Holiday end date cannot be earlier than the start date.")
        return end_date
