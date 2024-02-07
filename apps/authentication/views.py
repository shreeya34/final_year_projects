# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.

import csv
from datetime import datetime
from io import TextIOWrapper

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
import pandas as pd


# from apps.authentication.models import Profile

from apps.authentication.models import Profile
from .forms import LoginForm, SignUpForm
from django.contrib import messages
from django.contrib.auth.models import User
from .helper import send_forget_password_mail
from django.views import View
from .models import *
from apps.authentication.models import TestOrderTable
from .forms import UserProfileForm
import uuid
from .utils import log_activity


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
                request.session['is_logged_in'] = True
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})

def csv_view(request):
    uploaded_files = UploadedCSV.objects.filter(user=request.user)
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
    
    log_activity = ActivityLog.objects.all()# Log the activity
 
    return render(request, 'accounts/log.html',{'log_activity': log_activity})

def delete_log(request, log_id):
    log_activity = get_object_or_404(ActivityLog, id=log_id)
    log_activity.delete()
    return redirect('accounts/log.html')


from django.shortcuts import get_object_or_404

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
            else:
                messages.info(request, message='Something went wrong while sending the email.')
            
            return redirect('/forget-password/')
            
    except Exception as e:
        print(e)
    
    return render(request, 'accounts/forgetPassword.html')

def user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'home/user.html', {'form': form})
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
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')
            
            if user_id is  None:
                messages.success(request, 'No user id found.')
                return redirect(f'/change_password/{token}/')
                
            if  new_password != confirm_password:
                messages.success(request, 'both should  be equal.')
                return redirect(f'/change_password/{token}/')
            
            user_obj = User.objects.get(id = user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            
            return redirect('accounts/login/')
                    
    except Exception as e:
        print(e)
        
    return render(request , 'accounts/change_password.html' , context)

# file_upload_app/views.py
from django.shortcuts import render

from django.views.decorators.csrf import csrf_protect


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

# views.py

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

            
        







    

    
    
            
