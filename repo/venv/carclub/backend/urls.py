from django.urls import path

from django.contrib.auth import views as auth_views
from .import views

#this is only for development purposes right now
from django.conf import settings
from django.conf.urls.static import static

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
    path("garage/add_car", views.add_car_view, name="add_car"),

    #statistic pathing
    path("stats/", views.stats_view, name="stats"),

    #password reset pathing
    path('reset_password/', auth_views.PasswordResetView.as_view(), name ='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name = "password_reset_done.html"), name ='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name = "password_reset_confirm.html"), name ='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name = "password_reset_complete.html"), name ='password_reset_complete')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#the static at the end is only needed while in development, we can update this when we deploy it to the webserver