from django.db import models
from accounts.models import ShopProfile, CustomUser
from django.utils import timezone
from django.conf import settings
from cryptography.fernet import Fernet
# Subscriber model is now in the subscribers app


class MessageTemplate(models.Model):
    """Reusable message templates for shop owners."""
    TEMPLATE_TYPES = [
        ('sale', 'Sale Alert'),
        ('new_arrival', 'New Arrivals'),
        ('event', 'Special Event'),
        ('custom', 'Custom'),
    ]
    CATEGORY_CHOICES = [
        ('new_arrivals', 'New Arrivals'),
        ('sale_alert', 'Sale Alert'),
        ('promotional', 'Promotional'),
        ('custom', 'Custom')
    ]
    shop_profile = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=100)
    content = models.TextField()
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='custom')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='custom')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.shop_profile.shop_name}"


class Message(models.Model):
    """Represents a broadcast message sent or scheduled."""
    MESSAGE_TYPE_CHOICES = [
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('both', 'SMS & WhatsApp'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    shop_profile = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(max_length=1600)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='sms')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_for = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.message_type.upper()} - {self.content[:50]}"


class MessageLog(models.Model):
    """Logs each delivery attempt (anonymized — no phone numbers stored)."""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=50)
    channel = models.CharField(max_length=20)
    twilio_sid = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for message {self.message.id} - {self.status}"


class DeliveryReport(models.Model):
    """Delivery report for messages."""
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name='delivery_report')
    total_sent = models.IntegerField(default=0)
    successful = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)
    delivery_timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report for message {self.message.id}"


class DirectMessage(models.Model):
    """Direct messages between users (customers, support, etc)."""
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"


class Conversation(models.Model):
    """Group conversations/support tickets."""
    title = models.CharField(max_length=255)
    participants = models.ManyToManyField(CustomUser, related_name='conversations')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class ConversationMessage(models.Model):
    """Messages within a conversation."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username} in {self.conversation.title}"