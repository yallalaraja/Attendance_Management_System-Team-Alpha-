from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now
from datetime import datetime

class UserManager(BaseUserManager):
    def create_user(self, email, name, role='Employee', password=None):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email=email, name=name, role='Admin', password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Shift(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Employee')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    shift = models.ForeignKey(Shift, null=True, blank=True, on_delete=models.SET_NULL, related_name='users')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('On Leave', 'On Leave'),
    ]

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.name} - {self.date} - {self.status}"

    def get_total_hours(self):
        if self.check_in and self.check_out:
            check_in_dt = datetime.combine(self.date, self.check_in)
            check_out_dt = datetime.combine(self.date, self.check_out)
            duration = check_out_dt - check_in_dt
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            seconds = duration.seconds % 60
            return f"{hours} hours, {minutes} minutes, {seconds} seconds"
        return "N/A"

    def mark_check_in(self):
        """Mark current time as check-in if not already marked"""
        if not self.check_in:
            self.check_in = now().time()
            self.status = 'Present'
            self.save()

    def mark_check_out(self):
        """Mark current time as check-out if not already marked"""
        if not self.check_out:
            self.check_out = now().time()
            self.save()


from django.core.exceptions import ValidationError
from django.db import models

class LeaveRequest(models.Model):
    LEAVE_STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    LEAVE_TYPE = (
        ('Sick', 'Sick'),
        ('Casual', 'Casual'),
        ('Lop', 'Lop'),
    )

    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=LEAVE_STATUS, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')

    def clean(self):
        # Ensure that the employee cannot approve their own leave request
        if self.approved_by == self.employee:
            raise ValidationError("An employee cannot approve their own leave request.")

    def save(self, *args, **kwargs):
        # Call clean method to validate the condition before saving
        self.clean()
        super().save(*args, **kwargs)


class Holiday(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField(unique=True)
    end_date = models.DateField(unique=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.name} from {self.start_date} to {self.end_date}"


class UserShiftAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.name} → {self.shift.name} on {self.date}"
