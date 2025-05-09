from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Admin'


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Manager'


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Employee'


class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role in ['Admin', 'Manager']
