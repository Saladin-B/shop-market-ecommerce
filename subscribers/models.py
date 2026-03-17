from django.db import models
from django.contrib.auth.hashers import make_password
from accounts.models import ShopProfile


MONTH_CHOICES = [
    ('january', 'January'), ('february', 'February'), ('march', 'March'),
    ('april', 'April'), ('may', 'May'), ('june', 'June'),
    ('july', 'July'), ('august', 'August'), ('september', 'September'),
    ('october', 'October'), ('november', 'November'), ('december', 'December'),
]


class Subscriber(models.Model):
    """
    Privacy-first subscriber model.
    Phone numbers are encrypted/hashed; owners cannot view individual numbers.
    """
    shop = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, related_name='subscribers')
    # Encrypted phone number - owners CANNOT see individual numbers
    phone_number_encrypted = models.CharField(max_length=255)
    # Phone hash for lookup/unsubscribe (one-way hash)
    phone_number_hash = models.CharField(max_length=255)
    birth_month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    sms_consent = models.BooleanField(default=False)
    whatsapp_consent = models.BooleanField(default=False)

    class Meta:
        # Prevent duplicate subscriptions per shop
        unique_together = ('shop', 'phone_number_hash')

    def __str__(self):
        return f"Subscriber for {self.shop.shop_name} (subscribed {self.subscribed_at.date()})"