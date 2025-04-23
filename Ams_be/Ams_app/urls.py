from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,      # For obtaining a pair of access and refresh tokens
    TokenRefreshView,         # For refreshing the access token using a refresh token
)

from rest_framework.routers import DefaultRouter
from Ams_app.views import (
    UserViewSet,
    AttendanceViewSet,
    LeaveRequestViewSet,
    AttendanceReportViewSet,
    ShiftViewSet,
    HolidayViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'attendance-report', AttendanceReportViewSet, basename='attendance-report')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'holidays', HolidayViewSet, basename='holiday')

# Include the JWT token views
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls
