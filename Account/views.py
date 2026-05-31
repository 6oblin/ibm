import random  # Added for secure numeric pin sequence generation
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from .models import Item
from .forms import ItemForm, UserRegistrationForm

User = get_user_model()


def home(request):
    return render(request, 'Account/home.html')


def about(request):
    return HttpResponse("About Page")


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save user record structure but keep active permission restricted
            user = form.save(commit=False)
            user.is_active = False  
            
            # Generate a 6-digit dynamic numeric pin code string
            generated_otp = str(random.randint(100000, 999999))
            user.otp = generated_otp
            user.save()
            
            # --- SMTP Gmail OTP Packet Dispatched ---
            subject = 'Your Account Verification Code'
            message = f"Hi {user.username},\n\nThank you for registering. Your 6-digit verification code is:\n\n{generated_otp}\n\nPlease enter this code on the verification page to activate your profile."
            
            try:
                send_mail(subject, message, "p2017832@gmail.com", [user.email], fail_silently=False)
                # Keep username tracked in active session memory to secure target verification page
                request.session['otp_username'] = user.username
                messages.success(request, 'Registration successful! Please enter the 6-digit code sent to your email.')
                return redirect('verify_otp')
            except Exception:
                messages.error(request, 'Account created, but SMTP failed to send the OTP email.')
                user.delete()  # Fallback cleanup rollback to prevent orphan accounts
                return redirect('register')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    return render(request, 'Account/register.html', {'form': form})


def verify_otp(request):
    """View handling entry verification code processing checks"""
    username = request.session.get('otp_username')
    
    # Session boundary catch to prevent direct endpoint entry manipulation
    if not username:
        messages.error(request, "Session expired. Please register again.")
        return redirect('register')
        
    if request.method == "POST":
        user_input_otp = request.POST.get('otp_code')
        try:
            user = User.objects.get(username=username)
            
            # Compare character blocks directly
            if user.otp == user_input_otp:
                user.is_active = True
                user.is_verified = True
                user.otp = None  # Clear out temporary buffer register
                user.save()
                
                # Deallocate session registration trace boundaries
                del request.session['otp_username']
                
                messages.success(request, 'Your email has been verified! You can now log in.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
        except User.DoesNotExist:
            return redirect('register')
            
    return render(request, 'Account/verify_otp.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Enforce security check constraint on user profile baseline activation properties
            if not user.is_active:
                messages.error(request, 'Please verify your email address before logging in.')
                return redirect('login')
                
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            
            # 🌟 SYSTEM DASHBOARD ROUTING MATRIX
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')  # System Admins go to global monitor view
                
            # Clean string matching check to capture user roles safely
            user_role = getattr(user, 'role', '').upper()
            
            if user_role == 'OWNER':
                return redirect('business_dashboard')  # Business Owners go to AzBusiness app
                
            elif user_role == 'MANAGER':
                return redirect('manager_dashboard')   # Branch Managers
                
            elif user_role == 'EMPLOYEE':
                return redirect('dashboard')  # Frontline Staff
                
            elif user_role == 'CUSTOMER':
                return redirect('customer_portal')     # Consumer Facing Interface
                
            return redirect('dashboard')  # Standard inventory panel fallback for regular users
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'Account/login.html')


@login_required(login_url='login')
def dashboard(request):
    items = Item.objects.filter(user=request.user)
    grand_total = sum(item.quantity * item.price for item in items)
    return render(request, 'Account/dashboard.html', {'items': items, 'grand_total': grand_total})


# --- New Role-Specific Dashboard Placeholders ---

@login_required(login_url='login')
def manager_dashboard(request):
    """Control view for Outlet Managers"""
    return render(request, 'Account/manager_dashboard.html')


@login_required(login_url='login')
def employee_dashboard(request):
    """Logging dashboard for staff members"""
    return render(request, 'Account/dashboard.html')


@login_required(login_url='login')
def customer_portal(request):
    """Storefront or purchase history portal for clients"""
    return render(request, 'Account/customer_portal.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required(login_url='login')
def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, 'Item added successfully!')
            return redirect('dashboard')
    else:
        form = ItemForm()
    return render(request, 'Account/add_item.html', {'form': form})


@login_required(login_url='login')
def edit_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id, user=request.user)
    except Item.DoesNotExist:
        messages.error(request, 'Item not found or you do not have permission to edit it.')
        return redirect('dashboard')
        
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('dashboard')
    else:
        form = ItemForm(instance=item)
    return render(request, 'Account/edit_item.html', {'form': form})


@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id, user=request.user)
        item.delete()
        messages.success(request, 'Item deleted successfully!')
    except Item.DoesNotExist:
        messages.error(request, 'Item not found or you do not have permission to delete it.')
    
    return redirect('dashboard')