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
    last_login = models.DateTimeField(null=True)
    date_joined = models.DateTimeField(null=True)

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
    car_id = models.AutoField(primary_key=True)
    #this field is badly named, basically just there for foreign key stuff
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    #car info
    owner_name = models.CharField(max_length=100, null=True, blank=True)
    codriven = models.BooleanField(default=False, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True)
    picture = models.ImageField(upload_to='car_pictures/', null=True, blank=True)
    #extra fields for functionality
    favorite_car = models.BooleanField(default=False, blank=True)

    free_form_text = models.CharField(max_length=500, null=True)

    #to string function
    def __str__(self):
        return self.owner_name

#Tireset model to hold tires
class Tireset(models.Model):
    #primary key
    tireset_id = models.AutoField(primary_key=True)
    #foreign key to attach tires to the vehicle
    tire_vehicle = models.ForeignKey(Car, on_delete=models.CASCADE)
    #extra info that is nice to have on the tires
    date_driven =  models.DateField(null=True)
    highway_miles = models.IntegerField(null=True)
    weather_when_used = models.CharField(max_length=100, null=True, blank=True)

#tire model for database
class Tire(models.Model):
    #identifier info
    tire_id = models.AutoField(primary_key=True)
    #cascade to handle if tireset is deleted, tires will also be deleted
    tireset = models.ForeignKey(Tireset, on_delete=models.CASCADE, related_name='tires')
    #information about tire
    tire_picture = models.ImageField(upload_to='tire_pictures/', null=True, blank=True)
    tire_brand = models.CharField(max_length=100, null=True)
    tire_pressure = models.FloatField(null=True)
    tread_wear = models.CharField(max_length=255, null=True)

    #manufacturer info
    manufacturer_link = models.CharField(max_length=500, null=True, blank=True)
    manufacture_date = models.DateField(null=True)

#Record model to hold records
class Record(models.Model):
    #choices for record
    RECORD_TYPE_CHOICES = [
        ('Raw', 'Raw'),
        ('Pax', 'Pax'),
        ('Final', 'Final'),
    ]
    #primary key
    record_id = models.AutoField(primary_key=True)
    #foreign key to find it via owner
    record_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    #record info
    record_name = models.CharField(max_length=255)
    record_type = models.CharField(max_length=255, choices=RECORD_TYPE_CHOICES, null=True)
    record_date = models.DateField(null=True, blank=True)
    #link to the run
    video_link = models.CharField(max_length=100, null=True, blank=True)
    #tostring
    def __str__(self):
        return f"{self.record_type} - {self.record_date}"