from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from .forms import LoginForm, RegisterForm, ProfileUpdateForm


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
        form = ProfileUpdateForm(request.POST, instance=request.user)
        print('yippee"')
        if form.is_valid():
            print("print updated")
            form.save()
            messages.success(request, "You have successfully updated your profile!")
            return redirect('profile')  #redirect back to profile after saving changes
    else:
        form = ProfileUpdateForm(instance=request.user)#otherwise, just get current user info
    return render(request, 'profile.html', {'form': form, 'user': user})