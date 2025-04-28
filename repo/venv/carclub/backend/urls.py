from django.urls import path
from .import views
from .views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)

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
    path("garage/show_car/<int:car_id>", views.show_car_view, name="show_car"),
    path("garage/show_car/add_tires/<int:car_id>", views.add_tires_view, name="add_tires"),
    path("garage/show_car/edit_tires/<int:tireset_id>", views.edit_tires_view, name="edit_tireset"),

    #statistic pathing
    path("stats/", views.stats_view, name="stats"),
    path("stats/add_record", views.add_record_view, name="add_record"),
    path("stats/show_record/<int:record_id>", views.show_record_view, name="show_record"),
    path("stats/delete_record/<int:record_id>", views.delete_record_view, name="delete_record"),

    #password reset pathing
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#the static at the end is only needed while in development, we can update this when we deploy it to the webserver