# AzBusiness/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BusinessProfile

def business_owner_required(view_func):
    """Custom decorator that ensures only verified Business Owners can view a page"""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'OWNER':
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. This dashboard is reserved for Business Owners only.")
        return redirect('dashboard')  # Redirects normal users back to their general dashboard
    return wrapper

@login_required(login_url='login')
@business_owner_required
def business_dashboard(request):
    """The secure dashboard environment accessible only by Business Owners"""
    try:
        business = request.user.business_profile
        return render(request, 'AzBusiness/business_dashboard.html', {'business': business})
    except BusinessProfile.DoesNotExist:
        messages.info(request, "Please complete your business profile registration first.")
        return redirect('setup_business')

@login_required(login_url='login')
def setup_business(request):
    """Form view where new Business Owners register their company details"""
    if request.user.role != 'OWNER':
        return redirect('dashboard')
        
    if request.method == "POST":
        name = request.POST.get('company_name')
        email = request.POST.get('business_email')
        reg_num = request.POST.get('registration_number')
        address = request.POST.get('address')
        
        BusinessProfile.objects.create(
            owner=request.user,
            company_name=name,
            business_email=email,
            registration_number=reg_num,
            address=address
        )
        messages.success(request, "Business profile created successfully!")
        return redirect('business_dashboard')
        
    return render(request, 'AzBusiness/setup_business.html')