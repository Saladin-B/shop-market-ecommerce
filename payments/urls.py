from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pricing/', views.pricing, name='pricing'),
    path('checkout/', views.create_checkout_session, name='checkout'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('webhook/', views.stripe_webhook, name='webhook'),
]