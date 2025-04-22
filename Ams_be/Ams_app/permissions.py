from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        emp = getattr(user, 'employee', None)

        # Managers can view/approve/reject all
        if emp and emp.role == 'Manager':
            return True

        # Employees can only view or edit their own leaves
        return obj.employee == emp
