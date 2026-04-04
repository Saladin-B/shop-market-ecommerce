from django.contrib import admin
from .models import WhatsAppAlert, Product, Cart, CartItem


@admin.register(WhatsAppAlert)
class WhatsAppAlertAdmin(admin.ModelAdmin):
    list_display = ['shop', 'phone_number', 'created_at']
    list_filter = ['shop', 'created_at']
    search_fields = ['shop__shop_name', 'phone_number']
    readonly_fields = ['created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'shop', 'price', 'stock', 'created_at']
    list_filter = ['shop', 'created_at']
    search_fields = ['name', 'shop__shop_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'shop', 'get_item_count', 'get_total', 'created_at']
    list_filter = ['shop', 'created_at']
    search_fields = ['user__email', 'shop__shop_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'get_subtotal']
    search_fields = ['product__name']
    readonly_fields = ['created_at']
