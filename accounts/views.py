from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import BuyerRegistrationForm, ShopOwnerRegistrationForm, CustomerRegistrationForm
from .models import CustomUser
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
        login_input = request.POST.get('username')  # Can be email or username
        password = request.POST.get('password')
        
        # First, try to authenticate with the input as username
        user = authenticate(request, username=login_input, password=password)
        
        # If that fails, try finding by email and authenticating
        if user is None:
            try:
                user_by_email = CustomUser.objects.get(email=login_input)
                user = authenticate(request, username=user_by_email.username, password=password)
            except CustomUser.DoesNotExist:
                user = None
        
        if user is not None:
            # Check if user has both buyer and shop accounts with same email
            accounts_with_email = CustomUser.objects.filter(email=user.email)
            
            if accounts_with_email.count() > 1:
                # Multiple accounts exist - show selection page
                request.session['temp_user_email'] = user.email
                request.session['temp_password'] = password
                return redirect('accounts:select_account', email=user.email)
            
            # Single account - proceed with login
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            # Redirect based on role: buyers go to products, shop owners go to dashboard
            if user.role == 'customer':
                return redirect('payments:products')
            else:
                return redirect('dashboard:home')
        else:
            messages.error(request, "Invalid email/username or password.")
    
    return render(request, 'accounts/login.html')


@require_http_methods(["GET", "POST"])
def select_account(request, email):
    """Allow user to select which account to login to if they have multiple."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    accounts = CustomUser.objects.filter(email=email)
    
    if accounts.count() < 2:
        messages.error(request, "No multiple accounts found for this email.")
        return redirect('accounts:login')
    
    if request.method == 'POST':
        selected_username = request.POST.get('account')
        password = request.session.get('temp_password')
        
        user = authenticate(request, username=selected_username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            # Redirect based on role
            if user.role == 'customer':
                return redirect('payments:products')
            else:
                return redirect('dashboard:home')
        else:
            messages.error(request, "Authentication failed. Please try again.")
            return redirect('accounts:login')
    
    # Clear sensitive session data after use
    if 'temp_password' in request.session:
        del request.session['temp_password']
    
    return render(request, 'accounts/select_account.html', {
        'email': email,
        'accounts': accounts
    })


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