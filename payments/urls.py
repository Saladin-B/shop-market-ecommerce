from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('products/', views.products, name='products'),
    path('products/<uuid:shop_id>/', views.product_list, name='product_list'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.my_cart, name='my_cart'),
    path('cart/<int:cart_id>/', views.view_cart, name='view_cart'),
    path('cart/item/<int:item_id>/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/item/<int:item_id>/remove/', views.remove_from_cart, name='remove_from_cart'),
    
    # Stripe checkout
    path('checkout/<int:cart_id>/', views.create_checkout_session, name='checkout'),
    path('success/', views.checkout_success, name='success'),
    path('cancel/', views.checkout_cancel, name='cancel'),
]