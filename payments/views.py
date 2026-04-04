from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from accounts.models import ShopProfile
from .models import Product, Cart, CartItem, Order, OrderItem
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def products(request):
    """Display all products for authenticated users."""
    # Get products - show all available products
    products = Product.objects.all().select_related('shop')
    
    user_cart = None
    user_shop = None
    
    # Try to get user's ShopProfile
    try:
        user_shop = ShopProfile.objects.filter(owner=request.user).first()
        if user_shop:
            # Get user's first cart (if any)
            user_cart = Cart.objects.filter(user=request.user, shop=user_shop).first()
    except ShopProfile.DoesNotExist:
        pass
    
    return render(request, 'products/product_list.html', {
        'products': products,
        'user_cart': user_cart,
        'user_shop': user_shop
    })


def product_list(request, shop_id):
    """Display products for a shop."""
    shop = get_object_or_404(ShopProfile, id=shop_id)
    products = shop.products.all()
    return render(request, 'products/product_list.html', {
        'shop': shop,
        'products': products
    })


@login_required
def add_to_cart(request, product_id):
    """Add product to cart."""
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


@login_required
def view_cart(request, cart_id):
    """View shopping cart."""
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    return render(request, 'products/cart.html', {'cart': cart})


@login_required
def update_cart_item(request, item_id):
    """Update item quantity in cart."""
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


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_id = cart_item.cart.id
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('payments:view_cart', cart_id=cart_id)


@login_required
def my_cart(request):
    """View current user's cart."""
    # Get or create user's first cart
    user_carts = Cart.objects.filter(user=request.user)
    if user_carts.exists():
        cart = user_carts.first()
    else:
        # If no cart, show empty cart message
        return render(request, 'products/empty_cart.html')
    return render(request, 'products/cart.html', {'cart': cart})


@login_required
@require_POST
def create_checkout_session(request, cart_id):
    """Create Stripe checkout session for cart."""
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    
    if cart.items.count() == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('payments:my_cart')
    
    try:
        # Create Order
        order = Order.objects.create(
            user=request.user,
            shop=cart.shop,
            total_amount=cart.get_total(),
            items_count=cart.get_item_count()
        )
        
        # Create OrderItems
        line_items = []
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            
            line_items.append({
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': item.product.name,
                        'description': item.product.description[:500] if item.product.description else '',
                        'images': [request.build_absolute_uri(item.product.image.url)] if item.product.image else [],
                    },
                    'unit_amount': int(item.product.price * 100),  # Convert to pence
                },
                'quantity': item.quantity,
            })
        
        # Create Stripe session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(f'/payments/success/?order_id={order.id}'),
            cancel_url=request.build_absolute_uri(f'/payments/cancel/?order_id={order.id}'),
            customer_email=request.user.email,
            metadata={'order_id': order.id}
        )
        
        # Save Stripe payment intent
        order.stripe_payment_intent = session.id
        order.save()
        
        return redirect(session.url, code=303)
        
    except Exception as e:
        messages.error(request, f'Error creating checkout: {str(e)}')
        return redirect('payments:view_cart', cart_id=cart.id)


@login_required
def checkout_success(request):
    """Handle successful Stripe payment."""
    order_id = request.GET.get('order_id')
    
    if not order_id:
        messages.error(request, 'Invalid order.')
        return redirect('payments:my_cart')
    
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order.status = 'completed'
        order.save()
        
        # Clear cart
        Cart.objects.filter(user=request.user, shop=order.shop).delete()
        
        messages.success(request, 'Payment successful! Thank you for your order.')
        return render(request, 'payments/success.html', {'order': order})
        
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('payments:my_cart')


@login_required
def checkout_cancel(request):
    """Handle cancelled Stripe payment."""
    order_id = request.GET.get('order_id')
    order = None
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.status = 'cancelled'
            order.save()
        except Order.DoesNotExist:
            pass
    
    messages.info(request, 'Payment cancelled.')
    return render(request, 'payments/cancel.html', {'order': order})
