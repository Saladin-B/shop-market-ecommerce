from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="accounts-index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.registration_choice, name="registration-choice"),
    path("register/buyer/", views.buyer_register, name="buyer-register"),
    path("register/shop/", views.shop_owner_register, name="shop-register"),
    path("profile/", views.profile_view, name="profile"),
]