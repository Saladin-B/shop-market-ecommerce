from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.home, name="home"),  # make sure dashboard/views.py has home()
]