from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('On Leave', 'On Leave'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.status}"
