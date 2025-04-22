from rest_framework import permissions

class IsAdminOrManagerOrSelf(permissions.BasePermission):
    """
    Allows access to admins, managers, or the employee themself.
    """

    def has_object_permission(self, request, view, obj):
        # Allow staff (admin), the approving manager, or the employee themselves
        return (
            request.user.is_staff or
            request.user.role == 'Manager' or
            obj.employee == request.user
        )
