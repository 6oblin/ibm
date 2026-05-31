# Outlets/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('management/branch/', views.manager_dashboard, name='manager_dashboard'),
    path('add/', views.add_outlet, name='add_outlet'),
]