from django.urls import path
from .views import (
    LeaveRequestListCreateView,
    LeaveRequestDetailView,
    LeaveApprovalView,
)

urlpatterns = [
    path('leave/', LeaveRequestListCreateView.as_view(), name='leave-list-create'),
    path('leave/<int:pk>/', LeaveRequestDetailView.as_view(), name='leave-detail'),
    path('leave/<int:pk>/approve/', LeaveApprovalView.as_view(), name='leave-approval'),
]
