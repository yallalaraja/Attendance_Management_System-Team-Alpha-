# Ams_app/permissions.py

from datetime import datetime, date
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Holiday, UserShiftAssignment


# ----- Role-Based Permissions ----- #

class IsAdmin(BasePermission):
    """Allows access only to Admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Admin'


class IsHR(BasePermission):
    """Allows access only to HR users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'HR'


class IsEmployee(BasePermission):
    """Allows access only to Employee users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Employee'


class IsAdminOrHR(BasePermission):
    """Allows access to Admin and HR users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.role in ['Admin', 'HR']
        )


# ----- Object-Level Permissions ----- #

class IsAdminOrSelf(BasePermission):
    """Allows Admin users or the user themselves to access the object."""
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user


class IsAdminHRorSelf(BasePermission):
    """Allows Admin, HR, or the employee themselves to access the object."""
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_staff or
            request.user.role == 'HR' or
            obj.employee == request.user
        )


# ----- Special Condition Permissions ----- #

class IsNotHoliday(BasePermission):
    """Allows actions only on non-holiday days."""
    def has_permission(self, request, view):
        today = date.today()
        return not Holiday.objects.filter(start_date__lte=today, end_date__gte=today).exists()


class IsWithinAssignedShiftTime(BasePermission):
    """
    Allows action only if the current time falls within the user's assigned shift for today.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        now = datetime.now().time()
        today = date.today()

        # Get today's shift assignment
        try:
            shift_assignment = UserShiftAssignment.objects.get(user=request.user, date=today)
            shift = shift_assignment.shift
        except UserShiftAssignment.DoesNotExist:
            return False  # No shift assigned today

        return shift.start_time <= now <= shift.end_time
