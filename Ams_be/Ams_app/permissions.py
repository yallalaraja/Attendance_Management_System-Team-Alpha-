from rest_framework import permissions

class IsAdminOrSelf(permissions.BasePermission):
    """
    Custom permission to allow users to access only their own data,
    unless they are admin/staff.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user
