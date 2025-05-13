from django import forms
from django.forms import PasswordInput
from .models import User, Attendance, LeaveRequest, Shift, Holiday
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth.password_validation import validate_password
from datetime import date

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'role', 'shift', 'password']
        widgets = {'password': PasswordInput()}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        EmailValidator()(email)
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)
        return password


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'role', 'shift', 'password']
        widgets = {'password': PasswordInput()}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        EmailValidator()(email)
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)
        return password

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    
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
        fields = ['name', 'start_date', 'end_date', 'description']

    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')

        # Ensure that the start_date is not before today's date
        if start_date < date.today():
            raise forms.ValidationError("Start date cannot be in the past.")

        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')

        # Ensure that if end_date is provided, it is not before the start_date
        if end_date and start_date:  # Check if both dates exist
            if end_date < start_date:
                raise forms.ValidationError("End date cannot be before the start date.")
        
        return end_date

