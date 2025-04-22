from django.urls import path
from .views import UserCreateView, UserListView

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),  # Admin only, list of users
    path('register/', UserCreateView.as_view(), name='user-create'),  # Open registration
]
