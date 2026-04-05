from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import BuyerRegistrationForm, ShopOwnerRegistrationForm, CustomerRegistrationForm
from django.http import HttpResponse
import functools


def buyer_only(view_func):
    """Decorator to restrict access to buyer accounts only."""
    @functools.wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if request.user.role != 'customer':
            messages.error(request, "This page is only for buyers. You have a shop owner account. Please create a separate buyer account to shop.")
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def shop_owner_only(view_func):
    """Decorator to restrict access to shop owner accounts only."""
    @functools.wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if request.user.role != 'shop_owner':
            messages.error(request, "This page is for shop owners only. Please create a separate shop owner account.")
            return redirect('payments:products')
        return view_func(request, *args, **kwargs)
    return wrapped_view

def index(request):
    """Placeholder view for accounts app index page."""
    return HttpResponse("Accounts app")


def registration_choice(request):
    """Display registration type choice page (buyer or shop owner)."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    return render(request, 'accounts/registration_choice.html')


def login_view(request):
    """Handle user login for both customers and shop owners."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            # Redirect based on role: buyers go to products, shop owners go to dashboard
            if user.role == 'customer':
                return redirect('payments:products')
            else:
                return redirect('dashboard:home')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('dashboard:home')


def buyer_register(request):
    """Handle buyer/customer registration. Buyer accounts are ONLY for purchasing - not for selling."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = BuyerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your buyer account is ready. You can now browse and purchase items.")
            return redirect('payments:products')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BuyerRegistrationForm()

    return render(request, 'accounts/buyer_register.html', {'form': form})


def shop_owner_register(request):
    """Handle shop owner registration. Shop owner accounts are ONLY for selling - not for buying."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = ShopOwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your shop account is ready. You can now manage your shop and products.")
            return redirect('dashboard:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ShopOwnerRegistrationForm()

    return render(request, 'accounts/shop_owner_register.html', {'form': form})


def register_view(request):
    """Legacy registration route - redirects to registration choice."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    return redirect('accounts:registration-choice')


@login_required
def profile_view(request):
    """View and update user profile based on role. Accounts are strictly separated by role."""
    if request.user.role == 'shop_owner':
        # Shop owner profile
        shop_profile = request.user.shop_profile
        return render(request, 'accounts/profile.html', {'profile': shop_profile})
    elif request.user.role == 'customer':
        # Buyer profile
        return render(request, 'accounts/customer_profile.html', {'user': request.user})
    else:
        messages.error(request, "Unknown account type.")
        return redirect('dashboard:home')