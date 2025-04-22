from django.urls import path
from . import views  # or specific views

urlpatterns = [
    path('', views.home, name='home'),  # replace with your actual view
]
