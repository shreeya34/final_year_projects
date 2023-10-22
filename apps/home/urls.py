# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    # Matches any html file
    #

    path("my-influx",views.get_influx_data,name="get_influx_data"),

    re_path(r'^.*\.*', views.pages, name='pages')

]
