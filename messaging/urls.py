from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Subscriber management
    path('subscribe/<str:shop_id>/', views.subscribe_page, name='subscribe'),
    path('unsubscribe/<str:shop_id>/<str:token>/', views.unsubscribe, name='unsubscribe'),
    
    # Message broadcasting
    path('send/', views.send_message, name='send_message'),
    path('history/', views.message_list, name='message_list'),
]