from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from datetime import datetime

from .models import User, Car, Tire, Tireset, Record
from .handlers import get_weather

#inherits from the base authentication form, just customizing it here
class LoginForm(AuthenticationForm):
    # username = forms.CharField(label="Username", max_length=25)
    # password = forms.CharField(widget=forms.PasswordInput, label="Password")


    username = forms.CharField(label="Username", max_length=25, widget=forms.TextInput(attrs={
        'class': 'login-form-control', 
        'placeholder': 'Enter your username'
    }))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={
        'class': 'login-form-control', 
        'placeholder': 'Enter your password'
    }))
    
    

#inherits from the base user creation form, just customizing it here
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'register-form-control', 'placeholder': 'Enter Username'}))
    email = forms.EmailField(max_length=255, required=True, widget=forms.EmailInput(attrs={'class': 'register-form-control', 'placeholder': 'Enter Email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'register-form-control', 'placeholder': 'Enter Password'}), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'register-form-control', 'placeholder': 'Confirm Password'}), label="Confirm Password")

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
    username = forms.CharField(
        max_length=50,
        required=True,
        label="Username",  # Explicit label
        widget=forms.TextInput(attrs={"class": "form-control profile-input"})
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={"class": "form-control profile-input"})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        label="Last Name",
        widget=forms.TextInput(attrs={"class": "form-control profile-input"})
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control profile-input"})
    )
    profile_picture = forms.ImageField(
        label="Profile Picture",
        widget=forms.FileInput(attrs={"class": "form-control profile-file-input"})
    )

    class Meta:#metatable data
        model = User#model form is using
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_picture']#fields from the model to get for form


#add car forms
class CarCreationForm(forms.ModelForm):
    owner_name = forms.CharField(
        max_length=100,
        required=True,
        error_messages={'required': 'Please enter the owner\'s name.'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100})
    )

    codriven = forms.NullBooleanField(
        required=True,
        error_messages={'required': 'Please select whether the car is co-driven.'},
        widget=forms.NullBooleanSelect(attrs={'class': 'form-select'})
    )

    brand = forms.CharField(
        max_length=100,
        required=True,
        error_messages={'required': 'Please enter the brand of the car.'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100})
    )

    picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    free_form_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'maxlength': 500
        })
    )

    class Meta:
        model = Car
        fields = ['owner_name', 'codriven', 'brand', 'picture', 'free_form_text']

    def save(self, commit=True):
        #Get the form data (cleaned data)
        car_instance = super().save(commit=False)
        # You can also modify other fields like setting default values
        if car_instance.codriven is None:
            car_instance.codriven = False  # Set a default value for codriven if None
        #Set the owner of the car to the user and save if they exist
        user = self.initial.get('user')
        if commit and user:
            car_instance.owner = user
            #save after this
            car_instance.save()
        elif not user:
            raise ValidationError("Owner is required for the car.")
        return car_instance

class CarEditForm(forms.ModelForm):
    owner_name = forms.CharField(
        max_length=100,
        required=True,
        error_messages={'required': 'Please enter the owner\'s name.'},
        widget=forms.TextInput(attrs={'class': 'form-control edit-car-control', 'maxlength': 100})
    )

    favorite_car = forms.NullBooleanField(
        required=False,
        widget=forms.NullBooleanSelect(attrs={'class': 'form-select edit-car-select'})
    )

    codriven = forms.NullBooleanField(
        required=True,
        error_messages={'required': 'Please select whether the car is co-driven.'},
        widget=forms.NullBooleanSelect(attrs={'class': 'form-select edit-car-select'})
    )

    brand = forms.CharField(
        max_length=100,
        required=True,
        error_messages={'required': 'Please enter the brand of the car.'},
        widget=forms.TextInput(attrs={'class': 'form-control edit-car-control', 'maxlength': 100})
    )

    picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control edit-car-control'})
    )

    free_form_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control edit-car-control',
            'rows': 4,
            'maxlength': 500
        })
    )

    class Meta:
        model = Car
        fields = ['owner_name', 'favorite_car', 'codriven', 'brand', 'picture', 'free_form_text']

class TiresetCreationForm(forms.ModelForm):
    #define the car passed in to be used later in saving the object
    def __init__(self, *args, car=None, **kwargs):
        self.car = car
        super().__init__(*args, **kwargs)
    class Meta:
        model = Tireset
        fields = ['date_driven', 'highway_miles']
        widgets = {
            'date_driven': forms.SelectDateWidget(
                empty_label=("Choose Year", "Choose Month", "Choose Day"),
                years=range(2019, 2026)
            ),
            'highway_miles': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter highway miles'}),
        }
    def save(self, commit=True):
        #Get the form data (cleaned data)
        tireset_instance = super().save(commit=False)
        #raise error if car isn't here, otherwise set tireset car object to the passed car
        if not self.car:
            raise ValueError("Car is required for the tireset.")
        tireset_instance.tire_vehicle = self.car

        #if date given, get weather for that date
        if tireset_instance.date_driven:
            tireset_instance.weather_when_used = get_weather(tireset_instance.date_driven)
        else:
            tireset_instance.weather_when_used = "Unknown Weather"
        #save car and return it
        if commit:
            tireset_instance.save()
            print("Saving Tireset:", tireset_instance.pk)
        return tireset_instance

class TiresetEditForm(forms.ModelForm):
    #define the car passed in to be used later in saving the object
    class Meta:
        model = Tireset
        fields = ['date_driven', 'highway_miles', 'weather_when_used']
        widgets = {
            'date_driven': forms.SelectDateWidget(
                empty_label=("Choose Year", "Choose Month", "Choose Day"),
                years=range(2019, 2026)
            ),
            'highway_miles': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter highway miles'}),
            'tread_wear': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter tread wear info'}),

        }
    def save(self, commit=True):
        #Get the form data (cleaned data)
        tireset_instance = super().save(commit=False)
        #if date given, get weather for that date
        #save car and return it
        if commit:
            tireset_instance.save()
            print("Saving Tireset:", tireset_instance.pk)
        return tireset_instance

class TireCreationForm(forms.ModelForm):
    class Meta:
        model = Tire
        fields = ['tire_picture', 'tire_pressure', 'tread_wear', 'manufacture_date', 'manufacturer_link']
        widgets = {
            'manufacture_date': forms.SelectDateWidget(
                empty_label=("Choose Year", "Choose Month", "Choose Day"),
                years=range(2019, 2026)
            ),
            'tire_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'tire_pressure': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter tire pressure'}),
            'tread_wear': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter tread wear info'}),
            'manufacturer_link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter manufacturer link'}),
        }
#stats forms

class AddRecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['record_name', 'record_type', 'record_date', 'video_link']
        widgets = {
            'record_date': forms.SelectDateWidget(
                empty_label=("Choose Year", "Choose Month", "Choose Day"),
                years=range(2019, 2026),
                attrs={'class': 'form-select'}
            ),
            'record_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a record name'}),
            'record_type': forms.Select(attrs={'class': 'form-select'}),  # For ChoiceFields or ModelChoiceFields
            'video_link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter youtube.com link.'}),
        }
    def save(self, commit=True):
        #Get the form data (cleaned data)
        record_instance = super().save(commit=False)
        #Set the owner of the record to the user
        user = self.initial.get('user')
        if user:
            record_instance.record_owner = user
        else:
            raise ValidationError("Owner is required for the record.")
        #now save the record
        if commit:
            record_instance.save()
        print(record_instance)
        return record_instance
    

class EditRecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['record_name', 'record_type', 'record_date', 'video_link']
        widgets = {
            'record_date': forms.SelectDateWidget(
                empty_label=("Choose Year", "Choose Month", "Choose Day"),
                years=range(2019, 2026),
                attrs={'class': 'form-select'}
            ),
            'record_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a record name'}),
            'record_type': forms.Select(attrs={'class': 'form-select'}),  # For ChoiceFields or ModelChoiceFields
            'video_link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter youtube.com link.'}),
        }