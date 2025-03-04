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
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    #extra permissions
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    #logging fields
    last_login = models.CharField(max_length=100)
    date_joined = models.CharField(max_length=100)

    #extra user fields
    profile_picture = models.ImageField(upload_to='profile_pictures', null=True, blank=True)

    #to string function
    def __str__(self):
        return self.email
    
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
    car_id = models.IntegerField(primary_key=True)
    car_name = models.CharField(max_length=100)
    car_codriven = models.BooleanField(default=False)
    #Tire Id fields for the car
    left_front_tire = models.IntegerField()
    left_back_tire = models.IntegerField()
    right_front_tire = models.IntegerField()
    right_back_tire = models.IntegerField()

    #to string function
    def __str__(self):
        return self.car_name


