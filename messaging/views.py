from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import hashlib
from accounts.models import ShopProfile
from subscribers.models import Subscriber
from .forms import SubscriberForm


@require_http_methods(["GET", "POST"])
def subscribe_page(request, shop_id):
    """Public page for customers to subscribe to shop messages."""
    shop_profile = get_object_or_404(ShopProfile, unique_slug=shop_id)
    
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            phone = request.POST.get('phone_number')
            birth_month = form.cleaned_data['birth_month']
            
            # Encrypt phone before saving
            encrypted_phone = Subscriber.encrypt_phone(phone)
            subscriber, created = Subscriber.objects.get_or_create(
                shop=shop_profile,
                phone_number_encrypted=encrypted_phone,
                defaults={'birth_month': birth_month}
            )
            
            if not created:
                # Reactivate if previously unsubscribed
                subscriber.is_active = True
                subscriber.unsubscribed_at = None
                subscriber.birth_month = birth_month
                subscriber.save()
                message = 'Resubscribed successfully!'
            else:
                message = 'Subscribed successfully!'
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': message})
            else:
                return render(request, 'messaging/subscribe_success.html', {
                    'shop_name': shop_profile.shop_name,
                    'message': message
                })
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Form validation failed'}, status=400)
    else:
        form = SubscriberForm()
    
    return render(request, 'messaging/subscribe.html', {
        'form': form,
        'shop_name': shop_profile.shop_name,
        'shop_profile': shop_profile
    })


def unsubscribe(request, shop_id, token):
    """Unsubscribe from shop messages (one-click unsubscribe)."""
    shop_profile = get_object_or_404(ShopProfile, unique_slug=shop_id)
    
    # Find and deactivate subscriber
    subscribers = Subscriber.objects.filter(shop=shop_profile, is_active=True)
    for subscriber in subscribers:
        if verify_unsubscribe_token(subscriber, token):
            subscriber.is_active = False
            subscriber.save()
            return render(request, 'messaging/unsubscribe_success.html', {
                'shop_name': shop_profile.shop_name
            })
    
    return render(request, 'messaging/unsubscribe_error.html', status=404)


def verify_unsubscribe_token(subscriber, token):
    """Verify unsubscribe token for security."""
    import hashlib
    expected_token = hashlib.sha256(f"{subscriber.id}{subscriber.phone_number_encrypted}".encode()).hexdigest()
    return token == expected_token
