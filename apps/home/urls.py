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
    # path("numeric",views.get_mean_of_numeric_values,name="get_mean_of_numeric_values"),
    path("get_product_data",views.get_data_view,name="get_data_view"),
    path("search",views.search_products,name="search_products"),
    path("upload_csv",views.upload_to_influxdb,name="upload_to_influxdb"),
    re_path(r'^.*\.*', views.pages, name='pages')

]
