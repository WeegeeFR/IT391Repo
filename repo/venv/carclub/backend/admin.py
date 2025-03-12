from django.contrib import admin
from django.contrib.admin import AdminSite
from django.shortcuts import redirect

from .models import User, Car, Tire

class CustomAdminSite(AdminSite):
    site_header = "Car Club Administration"
    site_title = "Car Club Administration"
    index_title = "Welcome to the administration site!"

    def login(self, request, *args, **kwargs):
        #check if user is not staff
        if not request.user.is_staff:
            return redirect('home')  #redirect to homepage if not staff
        return super().login(request, *args, **kwargs)
    
admin_site = CustomAdminSite(name='car_club_admin')

#models to put on the site
admin_site.register(User)
admin_site.register(Car)
admin_site.register(Tire)
