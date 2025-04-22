# from django.shortcuts import render
# from django.http import HttpResponse

# # Create your views here.
# def home(request):
#     return HttpResponse("Welcome to the Attendance Management System!")

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
from .permissions import IsOwnerOrManager

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrManager]

    def get_queryset(self):
        user = self.request.user
        employee = user.employee
        
        if employee.role == 'Manager':
            # Manager sees all leave requests
            return LeaveRequest.objects.all()
        else:
            # Employee sees only their own leave requests
            return LeaveRequest.objects.filter(employee=employee)

    def perform_create(self, serializer):
        # Automatically assign current user as the employee applying for leave
        serializer.save(employee=self.request.user.employee)

    def update(self, request, *args, **kwargs):
        leave_request = self.get_object()
        new_status = request.data.get('status')

        # Only managers can approve/reject
        if new_status in ['Approved', 'Rejected']:
            if request.user.employee.role != 'Manager':
                return Response({"error": "Only managers can approve or reject leave."}, status=403)
            leave_request.status = new_status
            leave_request.approved_by = request.user.employee
            leave_request.save()
            return Response(self.get_serializer(leave_request).data)

        return super().update(request, *args, **kwargs)

