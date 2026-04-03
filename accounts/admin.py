from django.contrib import admin
from .models import CustomUser, ShopProfile


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'date_joined')
    list_filter = ('role', 'is_verified', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    fieldsets = (
        ('Account Info', {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture')}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_superuser', 'is_active', 'is_verified')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )


@admin.register(ShopProfile)
class ShopProfileAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'owner', 'unique_slug', 'subscription_tier', 'subscription_active')
    list_filter = ('subscription_tier', 'subscription_active', 'phone_number_verified')
    search_fields = ('shop_name', 'owner__username', 'owner__email')
    readonly_fields = ('unique_slug', 'created_at', 'updated_at', 'qr_code_display')
    fieldsets = (
        ('Shop Info', {'fields': ('owner', 'shop_name', 'shop_description', 'unique_slug')}),
        ('Images', {'fields': ('shop_logo',)}),
        ('Subscription', {'fields': ('subscription_tier', 'subscription_active')}),
        ('Verification', {'fields': ('phone_number_verified',)}),
        ('Payments', {'fields': ('stripe_customer_id',)}),
        ('QR Code', {'fields': ('qr_code_display',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def qr_code_display(self, obj):
        """Display QR code in admin"""
        try:
            qr_code_data = obj.generate_qr_code()
            if qr_code_data:
                return f'<img src="{qr_code_data}" width="200" height="200" />'
            return 'No QR code generated'
        except Exception as e:
            return f'Error: {str(e)}'
    qr_code_display.allow_tags = True
    qr_code_display.short_description = 'QR Code'
