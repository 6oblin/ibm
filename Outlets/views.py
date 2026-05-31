# Outlets/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Outlet, OutletStaff
from AzBusiness.views import business_owner_required  # 🌟 Imported safely from corporate app

# --- Custom Security Access Control Guards (Decorators) ---

def manager_required(view_func):
    """Decorator ensuring only users with the MANAGER role can view this dashboard"""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'role', '').upper() == 'MANAGER':
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Manager clearance credentials required.")
        return redirect('dashboard')
    return wrapper


# --- View Implementations ---

@login_required(login_url='login')
@manager_required
def manager_dashboard(request):
    """Isolated dashboard for location Managers to monitor their specific branch assignment"""
    try:
        # Fetch the physical location this manager is assigned to
        staff_profile = request.user.staff_assignment
        assigned_outlet = staff_profile.outlet
        
        # 🌟 Future Hook: Fetch items/inventory belonging only to this outlet branch
        # branch_items = assigned_outlet.items.all()
        
        context = {
            'outlet': assigned_outlet,
        }
        return render(request, 'Outlets/manager_dashboard.html', context)
        
    except OutletStaff.DoesNotExist:
        messages.error(request, "System Configuration Error: You are not assigned to any physical outlet branch.")
        return redirect('dashboard')


@login_required(login_url='login')
@business_owner_required
def add_outlet(request):
    """View allowing verified Business Owners to add physical outlets to their profile"""
    try:
        business = request.user.business_profile
    except AttributeError:
        messages.error(request, "You must create a business profile before adding outlets.")
        return redirect('setup_business')

    if request.method == "POST":
        name = request.POST.get('outlet_name')
        city = request.POST.get('city')
        address = request.POST.get('address')
        contact = request.POST.get('contact_number')

        if not name or not city:
            messages.error(request, "Outlet Name and City fields are required.")
            return render(request, 'Outlets/add_outlet.html')

        # Save the outlet row linked to the owner's enterprise database index
        Outlet.objects.create(
            business=business,
            name=name,
            city=city,
            address=address,
            contact_number=contact
        )
        
        messages.success(request, f"Outlet '{name}' has been successfully registered under your company.")
        return redirect('business_dashboard')

    return render(request, 'Outlets/add_outlet.html')