# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""


from django import views
from django.urls import path
from .views import ChangePassword, ForgetPassword, login_view, register_user, user_profile,csv_upload_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("forget-password/",ForgetPassword,name="ForgetPassword"),
    path('change-password/<token>/',ChangePassword,name="change_password"),
    path('profile/', user_profile, name='user_profile'),
    path('upload/', csv_upload_view, name='csv_upload_view'),
    
]
