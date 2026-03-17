from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class CustomUser(AbstractUser):
    """Extended user model for shop owners."""
    ROLE_CHOICES = [
        ('owner', 'Shop Owner'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='owner')
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class ShopProfile(models.Model):
    """Shop owner profile linked to CustomUser."""
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='shop_profile')
    shop_name = models.CharField(max_length=255)
    shop_description = models.TextField(blank=True)
    shop_logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    unique_slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    subscription_active = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shop_name} ({self.owner.email})"

    @property
    def subscription_page_url(self):
        """Returns the public subscription URL for this shop."""
        return f"/subscribe/{self.unique_slug}/"