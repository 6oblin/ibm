from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    
    # 🌟 CRITICAL CHANGE: The path for entering the 6-digit code
    path('verify-code/', views.verify_otp, name='verify_otp'),
    
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    path('add-item/', views.add_item, name='add_item'),
    path('edit-item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete-item/<int:item_id>/', views.delete_item, name='delete_item'),

    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('staff/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('portal/home/', views.customer_portal, name='customer_portal'),
]