from django.contrib import admin
from .models import (
    Subscriber, MessageTemplate, Message, MessageLog, 
    DirectMessage, Conversation, ConversationMessage, DeliveryReport
)

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['shop_profile', 'birth_month', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['shop_profile__shop_name']

@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'shop_profile', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'shop_profile__shop_name']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['shop_profile', 'status', 'message_type', 'created_at']
    list_filter = ['status', 'message_type', 'created_at']
    search_fields = ['shop_profile__shop_name', 'content']

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['message', 'status', 'channel', 'timestamp']
    list_filter = ['status', 'channel', 'timestamp']

@admin.register(DeliveryReport)
class DeliveryReportAdmin(admin.ModelAdmin):
    list_display = ['message', 'total_sent', 'successful', 'failed', 'delivery_timestamp']
    list_filter = ['delivery_timestamp']

@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'content']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'created_by__username']

@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'created_at']
    list_filter = ['created_at']
    search_fields = ['conversation__title', 'sender__username', 'content']
