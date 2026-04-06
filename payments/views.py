from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from functools import wraps
from accounts.models import ShopProfile
from .models import Product, Cart, CartItem


def buyer_only(view_func):
    """Decorator to restrict access to customer/buyer accounts only."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        # Only allow customer role
        if request.user.role != 'customer':
            messages.error(request, 'This feature is only available for buyer accounts.')
            return redirect('dashboard:home')
        
        return view_func(request, *args, **kwargs)
    return wrapped_view


@buyer_only
def products(request):
    """Display all products for buyer accounts only."""
    products = Product.objects.all()
    user_cart = None
    if request.user.shopprofile:
        # Get user's first cart (if any)
        user_cart = Cart.objects.filter(user=request.user).first()
    return render(request, 'products/product_list.html', {
        'products': products,
        'user_cart': user_cart
    })


def product_list(request, shop_id):
    """Display products for a shop."""
    shop = get_object_or_404(ShopProfile, id=shop_id)
    products = shop.products.all()
    return render(request, 'products/product_list.html', {
        'shop': shop,
        'products': products
    })


@buyer_only
def add_to_cart(request, product_id):
    """Add product to cart (buyer accounts only)."""
    product = get_object_or_404(Product, id=product_id)
    shop = product.shop
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user, shop=shop)
    
    # Get or create cart item
    quantity = int(request.POST.get('quantity', 1))
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('payments:view_cart', cart_id=cart.id)


@buyer_only
def view_cart(request, cart_id):
    """View shopping cart (buyer accounts only)."""
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    return render(request, 'products/cart.html', {'cart': cart})


@buyer_only
def update_cart_item(request, item_id):
    """Update item quantity in cart (buyer accounts only)."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated.')
    
    return redirect('payments:view_cart', cart_id=cart_item.cart.id)


@buyer_only
def remove_from_cart(request, item_id):
    """Remove item from cart (buyer accounts only)."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_id = cart_item.cart.id
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('payments:view_cart', cart_id=cart_id)


@buyer_only
def my_cart(request):
    """View current user's cart (buyer accounts only)."""
    # Get or create user's first cart
    user_carts = Cart.objects.filter(user=request.user)
    if user_carts.exists():
        cart = user_carts.first()
    else:
        # If no cart, show empty cart message
        return render(request, 'products/empty_cart.html')
    return render(request, 'products/cart.html', {'cart': cart})

