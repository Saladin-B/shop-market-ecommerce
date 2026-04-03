import stripe
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from decouple import config
from accounts.models import ShopProfile
from .models import Subscription

stripe.api_key = config('STRIPE_SECRET_KEY')


@login_required
def pricing(request):
    """Display pricing page."""
    try:
        shop = ShopProfile.objects.get(owner=request.user)
        subscription = Subscription.objects.get(shop=shop)
    except (Subscription.DoesNotExist, ShopProfile.DoesNotExist):
        subscription = None
    return render(request, 'payments/pricing.html', {'subscription': subscription})


@login_required
@require_POST
def create_checkout_session(request):
    """Create Stripe checkout session."""
    try:
        shop = ShopProfile.objects.get(owner=request.user)
    except ShopProfile.DoesNotExist:
        messages.error(request, 'You must have a shop profile.')
        return redirect('dashboard:home')
    
    plan = request.POST.get('plan')
    if plan not in ['basic', 'pro', 'enterprise']:
        messages.error(request, 'Invalid plan selected.')
        return redirect('payments:pricing')
    
    prices = {
        'basic': config('STRIPE_BASIC_PRICE_ID', default=''),
        'pro': config('STRIPE_PRO_PRICE_ID', default=''),
        'enterprise': config('STRIPE_ENTERPRISE_PRICE_ID', default=''),
    }
    
    if not prices[plan]:
        messages.error(request, 'Payment not configured.')
        return redirect('payments:pricing')
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': prices[plan], 'quantity': 1}],
            mode='subscription',
            customer_email=request.user.email,
            success_url=request.build_absolute_uri('/payments/success/'),
            cancel_url=request.build_absolute_uri('/payments/cancel/'),
            metadata={'shop_id': shop.id, 'plan': plan},
        )
        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('payments:pricing')


@login_required
def payment_success(request):
    """Payment success page."""
    return render(request, 'payments/success.html')


@login_required
def payment_cancel(request):
    """Payment cancelled page."""
    return render(request, 'payments/cancel.html')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = config('STRIPE_WEBHOOK_SECRET', default='')
    
    if not webhook_secret:
        return JsonResponse({'status': 'error'}, status=400)
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return JsonResponse({'status': 'error'}, status=400)
    
    if event['type'] == 'checkout.session.completed':
        _handle_checkout_completed(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        _handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        _handle_subscription_deleted(event['data']['object'])
    
    return JsonResponse({'status': 'success'})


def _handle_checkout_completed(session):
    """Handle successful checkout."""
    try:
        shop = ShopProfile.objects.get(id=session['metadata']['shop_id'])
        subscription, _ = Subscription.objects.get_or_create(shop=shop)
        subscription.stripe_subscription_id = session['subscription']
        subscription.plan = session['metadata']['plan']
        subscription.status = 'active'
        subscription.save()
    except Exception as e:
        print(f'Checkout error: {str(e)}')


def _handle_subscription_updated(sub):
    """Update subscription status."""
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=sub['id'])
        subscription.status = sub['status']
        subscription.save()
    except Subscription.DoesNotExist:
        pass


def _handle_subscription_deleted(sub):
    """Mark subscription as cancelled."""
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=sub['id'])
        subscription.status = 'cancelled'
        subscription.save()
    except Subscription.DoesNotExist:
        pass
