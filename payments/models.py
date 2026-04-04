from django.db import models
from accounts.models import ShopProfile, CustomUser


class WhatsAppAlert(models.Model):
    """Free WhatsApp alert subscription for fragrance shop customers."""
    shop = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, related_name='whatsapp_alerts')
    phone_number = models.CharField(max_length=20)  # Encrypted in messaging.Subscriber
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('shop', 'phone_number')

    def __str__(self):
        return f"{self.shop.shop_name} - {self.phone_number}"


class Product(models.Model):
    """Fragrance products sold by a shop."""
    shop = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.shop.shop_name} - {self.name}"


class Cart(models.Model):
    """Shopping cart for customers."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
    shop = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.shop.shop_name}"

    def get_total(self):
        """Calculate cart total."""
        return sum(item.get_subtotal() for item in self.items.all())

    def get_item_count(self):
        """Count items in cart."""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Individual items in a cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_subtotal(self):
        """Get subtotal for this item."""
        return self.product.price * self.quantity