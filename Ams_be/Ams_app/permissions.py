# Ams_app/permissions.py
from datetime import date
from rest_framework.permissions import BasePermission
from .models import Holiday

class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or getattr(request.user, 'role', '') in ['Admin', 'HR']
        )
    
from rest_framework import permissions

class IsAdminOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user
    
from rest_framework import permissions

class IsAdminOrManagerOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow staff (admin), the approving manager, or the employee themselves
        return (
            request.user.is_staff or
            request.user.role == 'HR' or
            obj.employee == request.user
        )
    

class IsNotHoliday(BasePermission):
    message = "Today is a holiday — no need to login or punch in."

    def has_permission(self, request, view):
        return not Holiday.objects.filter(date=date.today()).exists()
    

from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Admin'

class IsHR(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'HR'

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Employee'