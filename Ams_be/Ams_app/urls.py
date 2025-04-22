# Ams_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ShiftViewSet,
    HolidayViewSet,
    AttendanceListCreateView,
    AttendanceDetailView,
    LeaveRequestListCreateView,
    LeaveRequestDetailView,
    LeaveApprovalView,
)

# Router for ViewSets (for Shift & Holiday)
router = DefaultRouter()
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'holidays', HolidayViewSet, basename='holiday')

urlpatterns = [
    # DRF router endpoints (/api/shifts/, /api/holidays/)
    path('', include(router.urls)),
    # Attendance & Leave Management
    path('attendance/', AttendanceListCreateView.as_view(), name='attendance-list-create'),
    path('attendance/<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),
    path('leave/', LeaveRequestListCreateView.as_view(), name='leave-list-create'),
    path('leave/<int:pk>/', LeaveRequestDetailView.as_view(), name='leave-detail'),
    path('leave/<int:pk>/approve/', LeaveApprovalView.as_view(), name='leave-approval'),
]
