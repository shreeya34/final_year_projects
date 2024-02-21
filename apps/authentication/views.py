# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.

import csv
from datetime import datetime
from io import TextIOWrapper
import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
import pandas as pd


# from apps.authentication.models import Profile

from apps.authentication.models import Profile
from core import settings
from .forms import LoginForm, SignUpForm
from django.contrib import messages
from django.contrib.auth.models import User
from .helper import send_forget_password_mail
from django.views import View
from .models import *
from .utils import log_activity,CustomUserChangeForm
from .forms import UserProfileForm
import uuid
from core.influx import influx_client
from influxdb_client.client.write_api import SYNCHRONOUS
from django.contrib.auth.forms import UserChangeForm
from django.shortcuts import render

from django.views.decorators.csrf import csrf_protect


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['username'] = (username)
                request.session['user_id'] = (user.id)
                request.session['is_logged_in'] = True
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def logout_view(request):
    # Use the logout function to log out the user
    logout(request)
    # Redirect to a different page after logout (optional)
    return redirect('accounts/login.html') 

def csv_view(request):
    uploaded_files = UploadedCSV.objects.filter(user=request.user,is_deleted=False)
    return render(request, 'home/csvfile.html', {'uploaded_files': uploaded_files})

def my_view(request):
    # Save data to the session
    request.session['username'] = (username)
    request.session['is_logged_in'] = True

    # Access session data
    username = request.session.get('username')
    is_logged_in = request.session.get('is_logged_in')

    return render(request, 'accounts/login.html', {'username': username, 'is_logged_in': is_logged_in})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def activity_view(request):
  log_activity = ActivityLog.objects.filter(user=request.user) 
  return render(request, 'accounts/log.html',{'log_activity':log_activity})
 
def user_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated.')
            return redirect('profile')
    
        # form = UserChangeForm(request.user)
    return render(request, 'home/user.html')

def ForgetPassword(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            
            if not User.objects.filter(username=username).exists():
                messages.success(request, 'No user found with this username.')
                return redirect('/forget-password/')
            
            user_obj = User.objects.get(username=username)
            token = str(uuid.uuid4())
            
            # Get or create the profile object associated with the user
            profile_obj, created = Profile.objects.get_or_create(user=user_obj)
            
            # Access the actual Profile object from the tuple returned by get_or_create
            if not created:
                # If the profile already exists, update the forget_password_token
                profile_obj.forget_password_token = token
                profile_obj.save()
            else:
                # If the profile was just created, set the forget_password_token
                profile_obj = Profile.objects.get(user=user_obj)
                profile_obj.forget_password_token = token
                profile_obj.save()
            
            send_email = send_forget_password_mail(user_obj.email, token)
            
            if send_email:
                messages.success(request, 'An email is sent.')
                return render(request, 'accounts/forgetPassword.html')
            else:
                messages.info(request, message='Something went wrong while sending the email.')
            
            return redirect('/forget-password/')
            
    except Exception as e:
        print(e)
    
    return render(request, 'accounts/forgetPassword.html')


def ForgetPasswordPage(request):
    
    return (request, '/home/accounts/change_password.html')

def ChangePassword(request , token):
    context = {}
    
    try:
        profile_obj = Profile.objects.filter(forget_password_token = token).first()
        context = {'user_id' : profile_obj.user.id}
        print(request.method)
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            user_id = request.POST.get('user_id')
            
            if user_id is  None:
                messages.success(request, 'No user id found.')
                return redirect(f'/change-password/{token}/')
                
            if  new_password != confirm_password:
                messages.success(request, 'Password Confirmation do not match.')
                return redirect(f'/change-password/{token}/')
            
            user_obj = User.objects.get(id = user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            
            return redirect('accounts/login/')
                    
    except Exception as e:
        print(e)
        
    return render(request , 'accounts/change_password.html' , context)




def create_db(file_path):
    df = pd.read_csv(file_path, delimiter=',')
    list_of_csv = [list(row)for row in df.values]
    print(list_of_csv)
    
   

def csv_upload_view(request):
    if request.method =="POST":
        file = request.FILES['file']
        obj=File.objects.create(file=file)
        create_db(obj.file)
    return render (request,'home/index.html')

def handle_uploaded_file(uploaded_file):
    destination_directory = os.path.join(settings.BASE_DIR)

    # Ensure the destination directory exists; create if it doesn't
    # os.makedirs(destination_directory, exist_ok=True)

    # Define the file path in the destination directory
    try:
        destination_file_path = os.path.join(destination_directory, uploaded_file)
        os.unlink(destination_file_path)
        return True
    except Exception as e:
        pass
    # Move the uploaded file to the destination directory
    # with open(destination_file_path, 'wb') as destination:
    #     for chunk in uploaded_file.chunks():
    #         destination.write(chunk)
    # return destination_file_path

def delete_entry(request, entry_id):
    try:
        user_name = request.session.get('username')
        entry = UploadedCSV.objects.get(id=entry_id)

        uploaded_file = entry.csv_file.name

        if not uploaded_file:
            messages.error(request, 'Invalid file name')
            return redirect('csv_view')
            # return JsonResponse(data={"status": "error", "message": "Invalid file"}, safe=False)

        handle_uploaded_file(uploaded_file)

        # query_api = influx_client.query_api()

        # Construct delete query based on the file name
        # delete_query = f'from(bucket: "new_amazon") \
        #                 |> filter(fn: (r) => r["_measurement"] == "ecommerce_products") \
        #                 |> filter(fn: (r) => r["user"] == "{user_name}" and r["files"] == "{entry_id}") \
        #                 |> drop()'
        
        # delete_query = f'''
        #     import "influxdata/influxdb/monitor"
        #     monitor.from(bucket: "new_amazon")\
        #         |> filter(fn: (r) => r["_measurement"] == "ecommerce_products" and r["user"] == "{user_name}" and r["files"] == "{entry_id}")\
        #         |> drop()
        # '''

        # Execute the delete query
        # result = query_api.query(query=delete_query, org='93eb79fe52548977')
        # print("Delete Result: {0}".format(result))
        log_activity(request.user, "Deleted a file") 
        entry.is_deleted = True
        entry.save()
        # entry.delete()
        messages.success(request, 'Entry deleted successfully.')
    except UploadedCSV.DoesNotExist:
        messages.error(request, 'Entry not found.')
    
    return redirect('csv_view')


def display_asin(request):
    user_uploaded_csv = UploadedCSV.objects.filter(user=request.user)
    asins = []

    for uploaded_csv in user_uploaded_csv:
        csv_file = uploaded_csv.csv_file

        try:
            decoded_file = TextIOWrapper(csv_file.open(), encoding='utf-8')
            csv_reader = csv.DictReader(decoded_file)

            for row in csv_reader:
                asin = row.get('asin')  # Retrieve ASIN from the 'asin' column
                if asin:
                    asins.append(asin)

            decoded_file.close()
        except Exception as e:
            return HttpResponse(f"Error reading CSV file: {e}")

    return render(request, 'home/index.html', {'asins': asins})

            
        







    

    
    
            
