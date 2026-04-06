from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.utils import timezone
from django.db.models import Q
import hashlib
from accounts.models import ShopProfile
from subscribers.models import Subscriber
from .models import Message, DeliveryReport, DirectMessage
from .forms import SubscriberForm, MessageForm


@require_http_methods(["GET", "POST"])
def subscribe_page(request, shop_id):
    """Public page for customers to subscribe to shop messages."""
    shop_profile = get_object_or_404(ShopProfile, unique_slug=shop_id)
    
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            phone = request.POST.get('phone_number')
            birth_month = form.cleaned_data['birth_month']
            
            # Encrypt and hash phone before saving
            encrypted_phone = Subscriber.encrypt_phone(phone)
            phone_hash = Subscriber.hash_phone(phone)
            
            subscriber, created = Subscriber.objects.get_or_create(
                shop=shop_profile,
                phone_number_hash=phone_hash,
                defaults={
                    'phone_number_encrypted': encrypted_phone,
                    'birth_month': birth_month
                }
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

def buyer_messages_only(view_func):
    """Decorator to ensure users only access their own messages."""
    from functools import wraps
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapped_view


@login_required
@require_http_methods(["GET", "POST"])
def send_message(request):
    """Shop owner view to send broadcast messages to subscribers."""
    # Get shop profile for current user
    try:
        shop_profile = ShopProfile.objects.get(owner=request.user)
    except ShopProfile.DoesNotExist:
        django_messages.error(request, 'You must have a shop profile to send messages.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = MessageForm(request.POST, shop_profile=shop_profile)
        if form.is_valid():
            message = form.save(commit=False)
            message.shop_profile = shop_profile
            
            # Check if template was selected
            template_id = request.POST.get('use_template')
            if template_id:
                try:
                    template = shop_profile.templates.get(id=template_id)
                    message.content = template.content
                except:
                    pass
            
            # Set status based on schedule
            if message.scheduled_for:
                message.status = 'scheduled'
            else:
                message.status = 'sending'
            
            message.save()
            
            # Create delivery report
            subscribers_count = shop_profile.subscribers.filter(is_active=True).count()
            DeliveryReport.objects.create(
                message=message,
                total_sent=subscribers_count
            )
            
            # Send message synchronously (simple approach)
            if not message.scheduled_for:
                send_message_sync(message)
            
            django_messages.success(request, 'Message queued for sending!')
            return redirect('messaging:message_list')
    else:
        form = MessageForm(shop_profile=shop_profile)
    
    # Get subscriber count and QR code
    subscriber_count = shop_profile.subscribers.filter(is_active=True).count()
    templates = shop_profile.templates.all()
    
    # Generate QR code
    from .utils import generate_qr_code
    qr_code = generate_qr_code(shop_profile.unique_slug, request)
    
    return render(request, 'messaging/send_message.html', {
        'form': form,
        'templates': templates,
        'subscriber_count': subscriber_count,
        'shop_name': shop_profile.shop_name,
        'qr_code': qr_code,
        'shop_slug': shop_profile.unique_slug
    })


@login_required
@buyer_messages_only
def message_list(request):
    """View user's personal messages (received and sent)."""
    # Use Q objects to get messages where user is sender OR recipient
    # This creates a proper QuerySet that works with pagination
    messages_queryset = DirectMessage.objects.filter(
        Q(recipient=request.user) | Q(sender=request.user)
    ).order_by('-created_at')
    
    # Paginate results
    from django.core.paginator import Paginator
    paginator = Paginator(messages_queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'messaging/message_list.html', {
        'page_obj': page_obj,
        'page_title': 'My Messages'
    })


@login_required
@require_http_methods(["POST"])
@buyer_messages_only
def delete_message(request, message_id):
    """Delete a message (only if user is sender or recipient)."""
    message = get_object_or_404(DirectMessage, id=message_id)
    
    # Only allow sender or recipient to delete
    if message.sender != request.user and message.recipient != request.user:
        django_messages.error(request, 'You cannot delete this message.')
        return redirect('messaging:message_list')
    
    message.delete()
    django_messages.success(request, 'Message deleted successfully!')
    return redirect('messaging:message_list')


def send_message_sync(message):
    """Synchronous message sending (fallback if Celery not available)."""
    try:
        from twilio.rest import Client
        from django.conf import settings
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        subscribers = message.shop_profile.subscribers.filter(is_active=True)
        delivery_report = message.delivery_report
        successful = 0
        failed = 0
        
        for subscriber in subscribers:
            try:
                phone = Subscriber.decrypt_phone(subscriber.phone_number_encrypted)
                
                if message.message_type in ['sms', 'both']:
                    client.messages.create(
                        body=message.content,
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=phone
                    )
                
                if message.message_type in ['whatsapp', 'both']:
                    client.messages.create(
                        body=message.content,
                        from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                        to=f"whatsapp:{phone}"
                    )
                
                successful += 1
            except Exception as e:
                failed += 1
                print(f"Failed to send to {phone}: {str(e)}")
        
        # Update delivery report
        delivery_report.successful = successful
        delivery_report.failed = failed
        delivery_report.save()
        
        # Update message status
        message.status = 'sent'
        message.sent_at = timezone.now()
        message.save()
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")