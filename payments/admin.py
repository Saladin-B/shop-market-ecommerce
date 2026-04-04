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
    list_display = ['name', 'shop', 'price', 'stock', 'has_image', 'created_at']
    list_filter = ['shop', 'created_at']
    search_fields = ['name', 'shop__shop_name']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    fieldsets = (
        ('Product Info', {
            'fields': ('shop', 'name', 'description', 'price', 'stock')
        }),
        ('Image', {
            'fields': ('image', 'image_preview'),
            'description': 'Upload a JPG or PNG image. Images will be stored in media/products/'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_image(self, obj):
        """Show if product has an image"""
        return bool(obj.image)
    has_image.short_description = 'Has Image'
    has_image.boolean = True
    
    def image_preview(self, obj):
        """Display image preview in admin"""
        if obj.image:
            return f'<img src="{obj.image.url}" width="200" height="200" style="object-fit: cover; border-radius: 8px;"/>'
        return 'No image uploaded'
    image_preview.allow_tags = True
    image_preview.short_description = 'Image Preview'


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
