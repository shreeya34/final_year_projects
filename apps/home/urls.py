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
    path("upload_time",views.time_upload_to_influx,name="time_upload_to_influx"),
    path("/getAnnualData",views.get_annual_data,name="get_annual_data"),
    path("getAsinData",views.get_asin,name="get_asin"),
    path("stats_data",views.submitData,name="submitData"),
    path("categorydata",views.get_all_category_data,name="catogorydata"),
    path("get_category_data",views.get_category_data_by_name,name="get_category_data"),
    path("get_delete_data_by_file",views.delete_data_by_file,name="get_delete_data_by_file"),
    path("get_all_category_sales_count",views.get_all_category_sales_count,name="get_all_category_sales_count"),
    # path('csv_files', views.get_csv, name='csv_files'),
    re_path(r'^.*\.*', views.pages, name='pages'),

]
