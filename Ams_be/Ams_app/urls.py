from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShiftViewSet, HolidayViewSet

router = DefaultRouter()
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'holidays', HolidayViewSet, basename='holiday')

urlpatterns = [
    path('', include(router.urls)),
]
