from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['shop', 'plan', 'status', 'created_at']
    list_filter = ['status', 'plan']
    search_fields = ['shop__shop_name', 'stripe_subscription_id']
    readonly_fields = ['stripe_subscription_id', 'created_at']
