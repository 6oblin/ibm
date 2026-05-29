# AzBusiness/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('business/dashboard/', views.business_dashboard, name='business_dashboard'),
    path('business/setup/', views.setup_business, name='setup_business'),
]