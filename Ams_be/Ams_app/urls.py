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
router.register(r'attendances', AttendanceViewSet, basename='attendance')
router.register(r'attendances-report', AttendanceReportViewSet, basename='attendance-report')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'holidays', HolidayViewSet, basename='holiday')

urlpatterns = [
    # Template-based views (frontend)
    path('home/', views.home_view, name='home'),

    path('user/create/', views.create_user, name='create_user'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    path('attendance/check/', views.attendance_check, name='attendance_check'),
    path('attendance/status/', views.attendance_status, name='attendance_status'),
    path('attendance/list',views.attendance_list,name='attendance_list'),

    path('leave/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),  # Approve leave
    path('leave/reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('leave/apply/', views.apply_leave, name='apply_leave'),
    path('leave/list/', views.leave_list, name='leave_list'),

    path('shift/add/',views.add_shift,name='add_shift'),
    path('shift/list/', views.shift_list, name='shift_list'),
    path('shift/allocate',views.allocate_shift,name='shift_allocate'),

    path('holiday/', views.holiday_list, name='holiday_list'),
    path('holiday/add/', views.add_holiday, name='add_holiday'),


] + router.urls
