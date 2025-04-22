
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here
# Optional Role choices
ROLE_CHOICES = (
    ('Employee', 'Employee'),
    ('Manager', 'Manager'),
)

class Employee(models.Model):
   user = get_user_model()
   role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
   manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

   def __str__(self):
    return self.user.username

class LeaveRequest(models.Model):
    LEAVE_STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    LEAVE_TYPE = (
        ('Sick', 'Sick'),
        ('Casual', 'Casual'),
        ('Earned', 'Earned'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=LEAVE_STATUS, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')

    def __str__(self):
        return f"{self.employee.user.username} - {self.status}"


