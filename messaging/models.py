from django.db import models
from accounts.models import ShopProfile, CustomUser
from django.utils import timezone


class MessageTemplate(models.Model):
    """Reusable message templates for shop owners."""
    TEMPLATE_TYPES = [
        ('sale', 'Sale Alert'),
        ('new_arrival', 'New Arrivals'),
        ('event', 'Special Event'),
        ('custom', 'Custom'),
    ]
    shop = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='custom')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.shop.shop_name}"


class Message(models.Model):
    """Represents a broadcast message sent or scheduled."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('both', 'SMS & WhatsApp'),
    ]
    shop = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(max_length=1600)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='sms')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    total_recipients = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.shop.shop_name} [{self.status}] on {self.created_at.date()}"


class MessageLog(models.Model):
    """Logs each delivery attempt (anonymized — no phone numbers stored)."""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=50)
    channel = models.CharField(max_length=20)
    twilio_sid = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for message {self.message.id} - {self.status}"


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