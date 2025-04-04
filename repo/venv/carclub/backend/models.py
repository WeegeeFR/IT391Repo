from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


# Create your models here.

#User model for the database, overwrites django's default
class User(AbstractUser):
    #sign in info
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    #important info on account creation
    email = models.CharField(max_length=100, primary_key=True, unique=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)

    #extra permissions
    is_superuser = models.BooleanField(default=False)#gives every permission possible
    is_staff = models.BooleanField(default=False)#allows user to access admin site
    is_active = models.BooleanField(default=True)#set this to false to deactivate an account, don't remove from database

    #logging fields
    last_login = models.CharField(max_length=100)
    date_joined = models.CharField(max_length=100)

    #extra user fields
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    #to string function
    def __str__(self):
        return self.username
    
    #custom .clean function for email
    def clean(self):
        """
        Override the clean method to add custom validation logic.
        """
        super().clean() #call User's default clean logic

        # Check if the email is in a valid format or unique, etc.
        if not self.email:
            raise ValidationError('Email field cannot be empty.')

        # Custom logic for email format
        if '@' not in self.email:
            raise ValidationError('Enter a valid email address.')


#Car model
class Car(models.Model):
    #basic identifier info
    car_id = models.IntegerField(primary_key=True)
    #car info
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    codriven = models.BooleanField(null=True) #Allows true false and none
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='car_pictures/', null=True, blank=True)
    #Tire Id fields for the car
    left_front_tire = models.IntegerField(null=True)
    left_back_tire = models.IntegerField(null=True)
    right_front_tire = models.IntegerField(null=True)
    right_back_tire = models.IntegerField(null=True)

    #extra fields for functionality
    favorite_car = models.BooleanField(default=False)

    free_form_text = models.CharField(max_length=500)

    #to string function
    def __str__(self):
        return self.name

#tire model for database
class Tire(models.Model):
    #identifier info
    tire_id = models.IntegerField(primary_key=True)
    #cascade to handle if car is deleted, tires will also be deleted
    tire_vehicle = models.ForeignKey(Car, on_delete=models.CASCADE, null=True)
    date_driven =  models.DateField(null=True)
    tire_picture = models.ImageField(upload_to='tire_pictures/', null=True, blank=True)

    #information about tire
    tire_brand = models.CharField(max_length=100, null=True)
    tire_pressure = models.FloatField(null=True)
    tread_wear = models.CharField(max_length=255, null=True)
    highway_miles = models.IntegerField(null=True)

    #manufacturer info
    manufacturer_link = models.CharField(max_length=500, null=True)
    manufacture_date = models.DateField(null=True)
    
