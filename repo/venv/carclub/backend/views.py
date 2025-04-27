from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib import messages

from .forms import LoginForm, RegisterForm, ProfileUpdateForm, CarCreationForm, CarEditForm, TiresetCreationForm, TireCreationForm, TiresetEditForm, AddRecordForm, EditRecordForm
from .models import Car, Tire, Tireset, Record
from .handlers import scrape_season_events, get_records, get_links_from_string


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
    if request.method == "POST":
        print("post method")
        car_form = CarCreationForm(request.POST, request.FILES, initial={'user': request.user})
        if car_form.is_valid():
            #get newly added car
            car_form.save()
            #return to the garage with a message saying it newly added a car
            messages.success(request, "You have successfully added a vehicle!")
            return redirect('garage')
        else:
            print(car_form.errors)
            messages.error(request, "There was a problem creating the vehicle, please check the form for errors")
            car_form = CarCreationForm()
    else:
        car_form = CarCreationForm()
    return render(request, 'garage/add_car.html', {
        'car_form': car_form,
    })

@login_required
def show_car_view(request, car_id):
    #get current car from id
    current_car = get_object_or_404(Car, car_id=car_id)
    #get all tiresets associated with the car
    car_tiresets = Tireset.objects.filter(tire_vehicle=current_car)
    if request.method == 'POST':
        form = CarEditForm(request.POST, request.FILES, instance=current_car)
        if form.is_valid():
            form.save()
            return redirect('show_car', car_id=current_car.car_id)
    else:
        form = CarEditForm(instance=current_car)
    return render(request, 'garage/show_car.html', {'form': form, 'car': current_car, 'tiresets': car_tiresets})

@login_required
def add_tires_view(request, car_id):
    #get car from id
    car = get_object_or_404(Car, car_id=car_id)
    #Set prefixes for tire forms to match fields in template (not required if you're indexing)
    tire_prefixes = ['tire1', 'tire2', 'tire3', 'tire4']

    if request.method == 'POST':
        #Main tire set form
        tireset_form = TiresetCreationForm(request.POST, car=car)

        #Create tire forms with POST data
        tire_forms = [
            TireCreationForm(request.POST, request.FILES, prefix=prefix) for prefix in tire_prefixes
        ]

        #Validate all
        if tireset_form.is_valid() and all(form.is_valid() for form in tire_forms):
            tireset = tireset_form.save(commit=True)
            for i, form in enumerate(tire_forms):
                tire = form.save(commit=False)
                tire.tireset = tireset
                tire.save()
            
            messages.success(request, "You have successfully added a tireset to this vehicle!")
            return redirect('show_car', car_id=car.car_id)

    else:
        tireset_form = TiresetCreationForm(car=car)
        tire_forms = [
            TireCreationForm(prefix=prefix) for prefix in tire_prefixes
        ]

    context = {
        'car': car,
        'car_id': car_id,
        'tireset_form': tireset_form,
        'tire_forms': tire_forms,
    }
    return render(request, 'garage/add_tires.html', context)

@login_required
def edit_tires_view(request, tireset_id):
    #get car from tireset, and tireset from given id
    tireset = get_object_or_404(Tireset, tireset_id=tireset_id)
    car = tireset.tire_vehicle
    #Set prefixes for tire forms to match fields in template (not required if you're indexing)
    tire_prefixes = ['tire1', 'tire2', 'tire3', 'tire4']
    #get all four tires
    tires = list(tireset.tires.all())

    if request.method == 'POST':
        #create form with existing tireset data
        tireset_form = TiresetEditForm(request.POST, instance=tireset)

        #go through each tire and make form with the current tire data
        tire_forms = [
            TireCreationForm(request.POST, request.FILES, prefix=prefix, instance=tires[i])
            for i, prefix in enumerate(tire_prefixes)
        ]
        #check if everythings valid, then save the forms and redirect back
        if tireset_form.is_valid() and all(form.is_valid() for form in tire_forms):
            tireset = tireset_form.save()
            for form in tire_forms:
                form.save()
            messages.success(request, "Edited tireset successfully!")
            return redirect('show_car', car_id=car.car_id)

    else:
        tireset_form = TiresetEditForm(instance=tireset)
        tire_forms = [
            TireCreationForm(prefix=prefix, instance=tires[i])
            for i, prefix in enumerate(tire_prefixes)
        ]
    context = {
        'car': car,
        'tireset_form': tireset_form,
        'tire_forms': tire_forms,
    }
    return render(request, 'garage/edit_tires.html', context)

#Statistic page views
@login_required
def stats_view(request):
    #Check if the first button was pressed (e.g., by checking request GET or POST parameters)
    if request.method == 'POST' and 'get_events' in request.POST:
        # Generate the dictionary
        options_dict = scrape_season_events()
        # Store the dictionary in the session or pass it to the template context
        return render(request, 'stats/stats.html', {'options_dict': options_dict, 'show_dropdown': True, 'show_records': False})

    #Handle the second button press (after the dropdown menu is shown)
    elif request.method == 'POST' and 'selected_event' in request.POST:
        selected_event = request.POST.get('dropdown')
        selected_setting = request.POST.get('setting')  #radio button selection
        name = request.POST.get('name')
        car_make = request.POST.get('car_make')
        link_dictionary = get_links_from_string(selected_event)
        first_day_records = []
        second_day_records = []
        first_day_records = get_records(link_dictionary[selected_setting][0], name, car_make, selected_setting)
        if len(link_dictionary[selected_setting]) > 1:
            second_day_records = get_records(link_dictionary[selected_setting][1], name, car_make, selected_setting)

        #deal with adjusting table for amount of runs for html to display if the selected setting is 'final'
        first_day_runs = []
        second_day_runs = []
        if selected_setting == "Final":
            #if there's any for each day records, get how many there are and record it
            if len(first_day_records) > 0:
                for i in range(0, len(first_day_records[0][6:-2])):
                    current_run = "Run " + str(i+1)
                    first_day_runs.append(current_run)
            if len(second_day_records) > 0:
                for i in range(0, len(second_day_records[0][6:-2])):
                    current_run = "Run " + str(i+1)
                    second_day_runs.append(current_run)
        #return all the data
        return render(request, 'stats/stats.html', {'options_dict': scrape_season_events(), 
                                                    'first_records': first_day_records, 'second_records': second_day_records,
                                                    'show_dropdown': True, 'show_records': False, 'setting': selected_setting, 
                                                    'first_runs': first_day_runs, 'second_runs': second_day_runs})
    #handle case if user wants to show records
    elif request.method == 'POST' and 'show_records' in request.POST:
        #get all records of the user
        records = Record.objects.filter(record_owner=request.user)
        #render stats page with records
        return render(request, 'stats/stats.html', {'show_dropdown': True, 'show_records': True, 'records': records})

    #Default case when the page is first loaded
    return render(request, 'stats/stats.html', {'show_dropdown': False, 'show_records': False})

#view to handle adding a record for a user
@login_required
def add_record_view(request):
    user = request.user
    if request.method == 'POST':
        form = AddRecordForm(request.POST, initial={'user': user})
        if form.is_valid():
            form.save()
            messages.success(request, "Your record has been created successfully")
            records = Record.objects.filter(record_owner=request.user)
            return render(request, 'stats/stats.html', {'show_dropdown': True, 'show_records': True, 'records': records})
    else:
        form = AddRecordForm()
    return render(request, 'stats/add_record.html', {'form': form})

#view to handle showing off and allowing a user to edit 
@login_required
def show_record_view(request, record_id):
    #fetch record using id
    record = get_object_or_404(Record, pk=record_id)
    #parsing thel ink
    video_id = None
    if record.video_link and "watch?v=" in record.video_link:
        video_array = record.video_link.split("watch?v=")
        if video_array[1]:
            raw_id = video_array[1]
            video_id = raw_id.split("&")[0]  # strips extra URL params
    print(video_id)
    if request.method == 'POST':
        # Create a form instance with the existing record's data
        form = EditRecordForm(request.POST, instance=record)
        if form.is_valid():
            # Save the updated record
            form.save()
            #return back to the user's show record page.
            records = Record.objects.filter(record_owner=request.user)
            return render(request, 'stats/stats.html', {'show_dropdown': True, 'show_records': True, 'records': records})
    else:
        # For GET request, show the form with the current record data
        form = EditRecordForm(instance=record)
    return render(request, 'stats/show_record.html', {'form': form, 'record': record, 'video_id': video_id})

@login_required
def delete_record_view(request, record_id):
    #get the record to delete
    record = get_object_or_404(Record, pk=record_id)
    if request.method == 'POST':
        #just a little sanity check making sure the owner is indeed the owner before deleting
        if record.record_owner != request.user:
            messages.error(request, "You don't have permission to delete this record.")
            records = Record.objects.filter(record_owner=request.user)
            return render(request, 'stats/stats.html', {'show_dropdown': True, 'show_records': True, 'records': records})
        #delete record and send message saying its successfully deleted
        record.delete()
        messages.success(request, "Your record has been deleted successfully")
        #get records, render the stats page to return to the records page
        records = Record.objects.filter(record_owner=request.user)
        return render(request, 'stats/stats.html', {'show_dropdown': True, 'show_records': True, 'records': records})
    #it should literally never get here, send a message if it does
    messages.error(request, "Error deleting record.")
    records = Record.objects.filter(record_owner=request.user)
    return render(request, 'stats/stats.html', {'show_dropdown': True, 'show_records': True, 'records': records})