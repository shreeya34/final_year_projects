# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""


from django import views
from django.urls import path
from .views import ChangePassword, ForgetPassword, login_view, register_user,logout_view, user_profile,csv_upload_view,display_asin,csv_view,activity_view,delete_entry
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    # path("logout/", LogoutView.as_view(), name="logout"),
    path('logout/', logout_view, name='logout'),
    path("forget-password/",ForgetPassword,name="ForgetPassword"),
    path('change-password/<token>/',ChangePassword,name="ChangePassword"),
    path('profile', user_profile, name='profile'),
    path('upload', csv_upload_view, name='csv_upload_view'),
    path('csv_view',csv_view,name="csv_view"),
    path('csv_file',display_asin, name='display_asin'),
    path('activity_view',activity_view,name='activity_view'),
    path('delete_entry/<int:entry_id>/',delete_entry, name='delete_entry'),
   
    
]
