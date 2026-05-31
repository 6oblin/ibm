from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BusinessProfile

# --- Custom Security Access Control Guards (Decorators) ---

def admin_required(view_func):
    """Custom decorator that ensures only Superusers or Staff can view a page"""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. System Administration clearance required.")
        return redirect('dashboard')  # Redirects to standard user dashboard
    return wrapper


def business_owner_required(view_func):
    """Custom decorator that ensures only verified Business Owners can view a page"""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'OWNER':
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. This dashboard is reserved for Business Owners only.")
        return redirect('dashboard')
    return wrapper


# --- View Implementations ---

@login_required(login_url='login')
@admin_required
def admin_dashboard(request):
    """Global system control tower to view and manage every registered enterprise profile"""
    # Fetch all companies and optimize database hits by grabbing the owners in one query
    all_businesses = BusinessProfile.objects.all().select_related('owner')
    
    context = {
        'all_businesses': all_businesses,
        'total_businesses': all_businesses.count(),
    }
    return render(request, 'AzBusiness/admin_dashboard.html', context)


@login_required(login_url='login')
@business_owner_required
def business_dashboard(request):
    """The secure dashboard environment accessible only by Business Owners"""
    try:
        business = request.user.business_profile
        
        # 🌟 Future Integration Hook for your upcoming 'Outlets' app:
        # Once your Outlets app model has a ForeignKey linking to BusinessProfile 
        # using related_name='outlets', you can uncomment the line below:
        #
        # my_outlets = business.outlets.all()
        
        my_outlets = []  # Temporary placeholder array until Outlets app is live
        
        context = {
            'business': business,
            'outlets': my_outlets,
        }
        return render(request, 'AzBusiness/business_dashboard.html', context)
        
    except BusinessProfile.DoesNotExist:
        messages.info(request, "Please complete your business profile registration first.")
        return redirect('setup_business')


@login_required(login_url='login')
@business_owner_required
def setup_business(request):
    """Form view where new Business Owners register their company details"""
    
    # 🌟 FIXED ENTRY GUARD: Block both GET and POST requests if a profile already exists
    if hasattr(request.user, 'business_profile'):
        messages.warning(request, "You have already registered a business profile.")
        return redirect('business_dashboard')
        
    if request.method == "POST":
        name = request.POST.get('company_name')
        email = request.POST.get('business_email')
        reg_num = request.POST.get('registration_number')
        address = request.POST.get('address')
        
        # Use get_or_create to absolute protect your data layer from database race conditions
        business, created = BusinessProfile.objects.get_or_create(
            owner=request.user,
            defaults={
                'company_name': name,
                'business_email': email,
                'registration_number': reg_num,
                'address': address
            }
        )
        
        if created:
            messages.success(request, "Business profile created successfully!")
        return redirect('business_dashboard')
        
    return render(request, 'AzBusiness/setup_business.html')