from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ShopOwnerRegistrationForm
from .models import ShopProfile
from django.http import HttpResponse

def index(request):
    return HttpResponse("Accounts app")


def register_view(request):
    """Handle shop owner registration."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = ShopOwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to ShopConnect, {user.username}!")
            return redirect('dashboard:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ShopOwnerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """View and update shop profile."""
    shop_profile = request.user.shop_profile
    return render(request, 'accounts/profile.html', {'profile': shop_profile})