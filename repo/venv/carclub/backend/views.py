from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib import messages

from .forms import LoginForm, RegisterForm, ProfileUpdateForm, CarCreationForm, TireCreationForm
from .models import Car, Tire
from .handlers import scrape_season_events


# Create your views here.
def homepage_placeholder(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                login_message = "Welcome back, " + user.username
                messages.success(request, login_message)
                return redirect('home')  # Redirect to a page after login
            else:
                form.add_error(None, 'Invalid credentials')
    else:
        #create empty form if there's any other method
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created successfully!")
            return redirect('login')  # Redirect to the login page
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been succesfully logged out!")
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':#if user is changing info
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        print('yippee"')
        if form.is_valid():
            print("print updated")
            form.save()
            messages.success(request, "You have successfully updated your profile!")
            return redirect('profile')  #redirect back to profile after saving changes
    else:
        form = ProfileUpdateForm(instance=request.user)#otherwise, just get current user info
    return render(request, 'profile.html', {'form': form, 'user': user})

#garage views
@login_required
def garage_view(request):
    #get all cars, filters them to username, renders the template for the garage
    user = request.user
    cars = Car.objects.all().filter(owner=user)
    print(cars)
    return render(request, 'garage/garage.html', {'cars': cars})

@login_required
def add_car_view(request):
    #create forms, parameter in the form used to save data if the forms invalid for any reasons
    car_form = CarCreationForm(request.POST or None)
    tire_forms = [TireCreationForm(request.POST or None) for number in range(4)]
    user = request.user
    if request.method == "POST":
        print("post method")
        if car_form.is_valid():
            print('car is valid')
            #get newly added car
            added_car = car_form.save(commit=False)
            valid_tires_id = []
            valid_form_numbers = []
            form_dict = {}
            #go through each tire form, check if valid, get the tire_id of the form and the form number
            for i in range(len(tire_forms)):
                if tire_forms[i].is_valid():
                    current_tire = tire_forms[i].save()
                    form_dict[i] = current_tire.tire_id
            #go through valid form numbers, assign the tire id to the proper field in the added car object. 
            if form_dict[0]:
                added_car.left_front_tire = form_dict.get(0)
            if form_dict[1]:
                added_car.left_back_tire = form_dict.get(1)
            if form_dict[2]:
                added_car.right_front_tire = form_dict.get(2)
            if form_dict[3]:
                added_car.right_back_tire = form_dict.get(3)
            #return to the garage with a message saying it newly added a car
            messages.success(request, "You have successfully added a vehicle!")
            return redirect('garage')
        else:
            messages.error(request, "There was a problem creating the vehicle, please check the form for errors")
    return render(request, 'garage/add_car.html', {
        'car_form': car_form,
        'tire_forms': tire_forms
    })

#Statistic page views
@login_required
def stats_view(request):
    #Check if the first button was pressed (e.g., by checking request GET or POST parameters)
    if request.method == 'POST' and 'get_events' in request.POST:
        # Generate the dictionary
        options_dict = scrape_season_events()
        # Store the dictionary in the session or pass it to the template context
        request.session['options_dict'] = options_dict
        return render(request, 'stats/stats.html', {'options_dict': options_dict, 'show_dropdown': True})

    #Handle the second button press (after the dropdown menu is shown)
    elif request.method == 'POST' and 'selected_event' in request.POST:
        selected_value = request.POST.get('dropdown')
        print(selected_value)
        return HttpResponse("yippee")

    #Default case when the page is first loaded
    return render(request, 'stats/stats.html', {'show_dropdown': False})