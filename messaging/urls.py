from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('subscribe/<uuid:shop_id>/', views.subscribe_page, name='subscribe'),
    path('unsubscribe/<uuid:shop_id>/<str:token>/', views.unsubscribe, name='unsubscribe'),
]