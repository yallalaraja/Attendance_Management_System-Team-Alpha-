from django.urls import path
from rest_framework.routers import DefaultRouter
from Ams_app import views
from Ams_app.views import (
    UserViewSet,
    AttendanceViewSet,
    LeaveRequestViewSet,
    AttendanceReportViewSet,
    ShiftViewSet,
    HolidayViewSet,
)

# Set up router for viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'attendance-report', AttendanceReportViewSet, basename='attendance-report')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'holidays', HolidayViewSet, basename='holiday')

urlpatterns = [
    # Template-based views (frontend)
    path('home/', views.home_view, name='home'),
    
    path('user/create/', views.create_user, name='create_user'),
    path('login/', views.login_user, name='login'),

    path('attendance/check/', views.attendance_check, name='attendance_check'),
    path('attendance/history/', views.attendance_history, name='attendance_history'),


    path('leave/apply/', views.apply_leave, name='leave_request_form'),
    path('leave/list/', views.leave_list, name='leave_list'),


    path('shift/list/', views.shift_list, name='shift_list'),
    path('shift/allocate',views.allocate_shift,name='shift_allocate'),

    path('holiday/', views.holiday_list, name='holiday_list'),
    path('holiday/add/', views.add_holiday, name='add_holiday'),

    # API Endpoints (handled by DRF viewsets)
    # These paths are already handled by the router, so no need to redefine them.
    # The following paths are redundant with the DefaultRouter URLs:
    # 'attendance/', 'attendance-report/<int:user_id>/', etc.

] + router.urls
