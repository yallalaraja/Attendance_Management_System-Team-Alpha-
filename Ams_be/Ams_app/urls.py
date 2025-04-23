from django.urls import path
from rest_framework.routers import DefaultRouter
from Ams_app.views import (
    UserViewSet,
    AttendanceViewSet,
    LeaveRequestViewSet,
    AttendanceReportViewSet,
    ShiftViewSet,
    HolidayViewSet,
)

app_name = 'api'  # Namespace for this app

# Set up router for viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'attendance-report', AttendanceReportViewSet, basename='attendance-report')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'holidays', HolidayViewSet, basename='holiday')

urlpatterns = [
    # Attendance Management Paths
    path('check-in/', AttendanceViewSet.as_view({'post': 'mark_check_in'}), name='check_in'),
    path('check-out/', AttendanceViewSet.as_view({'post': 'mark_check_out'}), name='check_out'),

    # Attendance Report
    path('report/<int:user_id>/', AttendanceReportViewSet.as_view({'get': 'get_report'}), name='attendance_report'),

    # Leave Request Paths
    path('leave-request/', LeaveRequestViewSet.as_view({'post': 'create'}), name='create_leave_request'),
    path('leave-request/<int:pk>/', LeaveRequestViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='manage_leave_request'),

    # Shift and Holiday Management
    path('shift/', ShiftViewSet.as_view({'get': 'list', 'post': 'create'}), name='shift_list_create'),
    path('shift/<int:pk>/', ShiftViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='shift_manage'),

    path('holiday/', HolidayViewSet.as_view({'get': 'list', 'post': 'create'}), name='holiday_list_create'),
    path('holiday/<int:pk>/', HolidayViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='holiday_manage'),
] + router.urls
