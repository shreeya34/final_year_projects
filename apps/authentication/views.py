# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from profile import Profile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from django.contrib import messages
from django.contrib.auth.models import User
from .helper import send_forget_password_mail
import uuid


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
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


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

def ForgetPassword(request):
    try:
        if request.method == "POST":
            username = request.POST.get('username')
            
            if not User.objects.filter(username=username).first():
                messages.success(request,'user not found')
                return redirect('/forgetPassword')
            user_obj = User.objects.get(username=username)
            token = str(uuid.uuid4())
            profile_obj = Profile.objects.get(user=user_obj)
            profile_obj.forget_password_token =token
            profile_obj.save()
            send_forget_password_mail(user_obj, token)
            messages.success(request,'An email is send')
            return redirect('/forgetPassword/')
            
    except Exception as e:
        print(e)
        return render(request, 'accounts/forgetPassword.html')
    return render(request, 'accounts/forgetPassword.html')

def ChangePassword(request,token):
    contex = {}
    try:
        profile_obj=Profile.objects.filter(forget_password_token = token)
        contex = {'user_id': profile_obj.user_id}
        
        if request.method == 'POST':
            new_password = request.POST.get('new_Password')
            confirm_password = request.POST.get('confirm_password')
            user_id = request.POST.get('user_id')
            
            if user_id is None:
                  msg = 'No user id found'
                  return redirect('/change_password/')
              
            if new_password!= confirm_password:
                messages.success(request, 'both should be equal')
                return redirect(f'/change_password/{token}')
            
            user_id = User.objects.get(id = user_id)
            user_id.set_password(new_password)
            user_id.save()
            return redirect('/login/')
                
        
        
        
    except Exception as e:
        print(e)
    return render(request,'accounts/change_password.html',contex)
    
    
            
