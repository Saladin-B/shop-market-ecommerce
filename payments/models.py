from django.db import models
from accounts.models import ShopProfile


class Subscription(models.Model):
    """Stripe subscription record for shop owners."""
    PLAN_CHOICES = [
        ('basic', 'Basic - 500 msgs/month'),
        ('pro', 'Pro - 2000 msgs/month'),
        ('enterprise', 'Enterprise - Unlimited'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('cancelled', 'Cancelled'),
        ('past_due', 'Past Due'),
    ]
    shop = models.OneToOneField(ShopProfile, on_delete=models.CASCADE, related_name='subscription')
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    message_credits = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shop.shop_name} - {self.plan} ({self.status})"