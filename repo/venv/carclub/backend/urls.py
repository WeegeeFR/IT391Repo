from django.urls import path

from django.contrib.auth import views as auth_views
from .import views

urlpatterns = [
    #main pathing
    path('', views.homepage_placeholder, name="home"),

    #user pathing
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile_view, name="profile"),

    #garage pathing
    path("garage/", views.garage_view, name="garage"),

    #password reset pathing
    path('reset_password/', auth_views.PasswordResetView.as_view(), name ='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name = "password_reset_done.html"), name ='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name = "password_reset_confirm.html"), name ='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name = "password_reset_complete.html"), name ='password_reset_complete')
]