from django.contrib import admin
from .models import MessageTemplate, Message, MessageLog, DirectMessage, Conversation, ConversationMessage

@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'shop', 'template_type', 'created_at']
    list_filter = ['template_type', 'created_at']
    search_fields = ['name', 'shop__shop_name']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['shop', 'status', 'channel', 'total_recipients', 'successful_deliveries', 'created_at']
    list_filter = ['status', 'channel', 'created_at']
    search_fields = ['shop__shop_name', 'content']

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['message', 'status', 'channel', 'timestamp']
    list_filter = ['status', 'channel', 'timestamp']

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
