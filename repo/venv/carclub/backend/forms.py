from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from datetime import datetime

from .models import User, Car, Tire

#inherits from the base authentication form, just customizing it here
class LoginForm(AuthenticationForm):
    # username = forms.CharField(label="Username", max_length=25)
    # password = forms.CharField(widget=forms.PasswordInput, label="Password")


    username = forms.CharField(label="Username", max_length=25, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Enter your username'
    }))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Enter your password'
    }))
    
    

#inherits from the base user creation form, just customizing it here
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}))
    email = forms.EmailField(max_length=255, required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}), label="Confirm Password")

    # Custom validation for password matching
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match")
        return password2

    # Save the user to the database
    def save(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password1')

        #create the user instance but don't save yet
        user = User(username=username, email=email)
        user.set_password(password)  #Set the password
        user.date_joined = datetime.today().strftime('%Y-%m-%d')#set account creation date

        #save and return user
        user.save()
        return user
    

class ProfileUpdateForm(UserChangeForm):
    #Adding field info to the form
    username = forms.CharField(max_length=50)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(widget=forms.EmailInput())
    profile_picture = forms.ImageField(widget=forms.FileInput())
    class Meta:#metatable data
        model = User#model form is using
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_picture']#fields from the model to get for form


#add car forms
class CarCreationForm(forms.ModelForm):
    #can leave codriven as unknown if person cant remember
    codriven = forms.BooleanField(widget=forms.NullBooleanSelect)
    brand = forms.CharField(max_length=100)
    free_form_text = forms.CharField(widget=forms.Textarea, max_length=500)
    
    class Meta:
        model = Car
        fields = ['owner', 'codriven', 'brand', 'picture', 'free_form_text']


class TireCreationForm(forms.ModelForm):
    tire_pressure = forms.FloatField()
    tread_wear = forms.CharField(max_length=255)
    tread_wear = forms.CharField(max_length=255)
    highway_miles = forms.IntegerField()
    #widget to select date, empty_label to make it not required
    manufacture_date = forms.DateField(widget=forms.SelectDateWidget(empty_label=("Choose Year", "Choose Month", "Choose Day")))

    class Meta:
        model = Tire
        fields = ['tire_picture', 'tire_pressure', 'tread_wear', 'highway_miles', 'manufacture_date']