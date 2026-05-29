from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Item
from .forms import ItemForm, UserRegistrationForm


def home(request):
    return render(request, 'Account/home.html')


def about(request):
    return HttpResponse("About Page")


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    return render(request, 'Account/register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'Account/login.html')


@login_required(login_url='login')
def dashboard(request):
    items = Item.objects.filter(user=request.user)
    grand_total = sum(item.quantity * item.price for item in items)
    return render(request, 'Account/dashboard.html', {'items': items, 'grand_total': grand_total})


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
