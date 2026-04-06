from django.db import models
from django.contrib.auth.hashers import make_password
from accounts.models import ShopProfile
from django.conf import settings
from cryptography.fernet import Fernet
import hashlib


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
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Prevent duplicate subscriptions per shop
        unique_together = ('shop', 'phone_number_hash')

    def __str__(self):
        return f"Subscriber for {self.shop.shop_name} (subscribed {self.subscribed_at.date()})"

    @staticmethod
    def encrypt_phone(phone_number):
        """Encrypt phone number using Fernet encryption."""
        try:
            cipher = Fernet(settings.ENCRYPTION_KEY.encode())
            encrypted = cipher.encrypt(phone_number.encode())
            return encrypted.decode()
        except Exception:
            # Fallback if encryption fails
            return phone_number

    @staticmethod
    def decrypt_phone(encrypted_phone):
        """Decrypt phone number."""
        try:
            cipher = Fernet(settings.ENCRYPTION_KEY.encode())
            decrypted = cipher.decrypt(encrypted_phone.encode())
            return decrypted.decode()
        except Exception:
            # Fallback if decryption fails
            return encrypted_phone

    @staticmethod
    def hash_phone(phone_number):
        """Create a one-way hash of phone number for lookup."""
        return hashlib.sha256(phone_number.encode()).hexdigest()