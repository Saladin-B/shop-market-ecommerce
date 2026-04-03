"""
Celery tasks for asynchronous message sending.
"""
from celery import shared_task
from django.conf import settings
from .models import Message, Subscriber
from django.utils import timezone


@shared_task(bind=True, max_retries=3)
def send_message_async(self, message_id):
    """
    Async task to send messages to all active subscribers.
    Retries up to 3 times on failure with exponential backoff.
    """
    try:
        from twilio.rest import Client
        
        message = Message.objects.get(id=message_id)
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Get all active subscribers
        subscribers = message.shop_profile.subscribers.filter(is_active=True)
        delivery_report = message.delivery_report
        
        successful = 0
        failed = 0
        
        for subscriber in subscribers:
            try:
                # Decrypt phone number
                phone = Subscriber.decrypt_phone(subscriber.phone_number_encrypted)
                
                # Send SMS if requested
                if message.message_type in ['sms', 'both']:
                    client.messages.create(
                        body=message.content,
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=phone
                    )
                
                # Send WhatsApp if requested
                if message.message_type in ['whatsapp', 'both']:
                    client.messages.create(
                        body=message.content,
                        from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                        to=f"whatsapp:{phone}"
                    )
                
                successful += 1
                
            except Exception as e:
                failed += 1
                print(f"Failed to send to subscriber {subscriber.id}: {str(e)}")
        
        # Update delivery report
        delivery_report.successful = successful
        delivery_report.failed = failed
        delivery_report.save()
        
        # Update message status
        message.status = 'sent'
        message.sent_at = timezone.now()
        message.save()
        
        return {
            'status': 'success',
            'message_id': message_id,
            'successful': successful,
            'failed': failed
        }
        
    except Message.DoesNotExist:
        print(f"Message with id {message_id} not found")
        return {'status': 'error', 'message': 'Message not found'}
    
    except Exception as exc:
        # Retry with exponential backoff (5s, 25s, 125s)
        raise self.retry(exc=exc, countdown=5 ** self.request.retries)


@shared_task
def send_scheduled_messages():
    """
    Periodic task to check and send scheduled messages.
    Should be run every minute via Celery Beat.
    """
    from django.utils import timezone
    
    # Find messages scheduled for now
    now = timezone.now()
    scheduled_messages = Message.objects.filter(
        status='scheduled',
        scheduled_for__lte=now
    )
    
    count = 0
    for message in scheduled_messages:
        send_message_async.delay(message.id)
        count += 1
    
    return f"Queued {count} scheduled messages for sending"
