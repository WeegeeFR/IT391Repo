from django.urls import path
from .import views

urlpatterns = [
    path('', views.homepage_placeholder, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register")
]