from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
from .permissions import IsAdminOrManagerOrSelf

class LeaveRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Admin' or user.role == 'Manager':
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.filter(employee=user)

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

class LeaveRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManagerOrSelf]

class LeaveApprovalView(generics.UpdateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        leave = self.get_object()

        if request.user.role != 'Manager':
            return Response({'detail': 'Only managers can approve/reject leaves.'}, status=status.HTTP_403_FORBIDDEN)

        status_value = request.data.get('status')
        if status_value not in ['Approved', 'Rejected']:
            return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        leave.status = status_value
        leave.approved_by = request.user
        leave.save()
        return Response({'detail': f'Leave {status_value.lower()}.'})
