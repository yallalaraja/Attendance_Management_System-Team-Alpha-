# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
# from .forms import RegisterForm, LoginForm
# from .models import User

# def register_view(request):
#     if request.method == "POST":
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect("login")
#     else:
#         form = RegisterForm()
#     return render(request, "users/register.html", {"form": form})

# def login_view(request):
#     if request.method == "POST":
#         form = LoginForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect("dashboard")
#     else:
#         form = LoginForm()
#     return render(request, "users/login.html", {"form": form})

# def logout_view(request):
#     logout(request)
#     return redirect("login")

# @login_required
# def dashboard_view(request):
#     role = request.user.role
#     if role == 'admin':
#         return render(request, "users/dashboard.html", {"message": "Welcome Admin!"})
#     elif role == 'teacher':
#         return render(request, "users/dashboard.html", {"message": "Welcome Teacher!"})
#     elif role == 'student':
#         return render(request, "users/dashboard.html", {"message": "Welcome Student!"})
#     else:
#         return render(request, "users/dashboard.html", {"message": "Unknown role!"})

# Ams_app/views.py
from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Attendance
from .serializers import AttendanceReportSerializer
from .permissions import IsAdminOrManager

class AttendanceReportView(generics.ListAPIView):
    serializer_class = AttendanceReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManager]

    def get_queryset(self):
        employee_id = self.request.query_params.get('employee_id')
        if not employee_id:
            raise PermissionDenied("Please provide an employee_id in query params.")

        last_30_days = timezone.now().date() - timedelta(days=30)
        return Attendance.objects.filter(user__id=employee_id, date__gte=last_30_days)
