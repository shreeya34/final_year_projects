# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import datetime, timedelta

import http
from http import client
from io import TextIOWrapper
import json
import os
import random
from django.conf import settings
from django.shortcuts import redirect, render
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from core.influx import influx_client
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from django.conf import settings
import csv   
import requests
from .models import get_product_info
from apps.authentication.models import UploadedCSV
from apps.authentication.forms import CSVUploadForm
from pmdarima import auto_arima
import pandas as pd
from apps.authentication.utils import log_activity

from django.core.management.base import BaseCommand
from django.contrib import messages

BUCKET_NAME = settings.INFLUXDB_SETTINGS['bucket']
ORG_NAME = settings.INFLUXDB_SETTINGS['org']


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


def get_influx_data(request): #old way to upload static files
    
    # check_health = influx_client.health()
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    csv_file = 'ecommerce_data.csv'  # Replace with the path to your CSV file
    # # csv_file = request.params
    data_points = []
    fields = None  # Initialize fields as None
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Create a Point for each row in the CSV
            point = influxdb_client.Point(row['_measurement']) \
                .tag("asin", row['asin']) \
                .tag("product_name", row['product_name']) \
                .tag("category", row['category']) \
                .field(row['_field'], float(row['_value'])) \
                .time(row['_time'], influxdb_client.WritePrecision.NS)
            try:
                # Write the point to the specified bucket
                write_api.write(bucket=BUCKET_NAME, org=ORG_NAME, record=point)
            except Exception as e:
                print(f"Failed to write: {e}")
        

    return JsonResponse({'success':True, 'message':"Data Written Succesfully to Influx"})
            
def get_cookie_dates(request):
     # Get the current date and time
    end_time = datetime.now()

    # Calculate the start time (last one month)
    start_time = end_time - timedelta(days=180)

    # Format the start time and end time as strings in '%Y-%m-%d %H:%M:%S' format
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    start_time = request.COOKIES.get('start_time', start_time_str)
    end_time = request.COOKIES.get('end_time', end_time_str)
    return start_time, end_time

def search_products(request): 

    asin = request.GET.get('asin')
   
    product_name = request.GET.get('product_name')
    user_name = request.session.get('username')
    category = request.GET.get('category')
    start_time, end_time = get_cookie_dates(request)
    query_api = influx_client.query_api()
    if asin not in ['','null']:
        query = f'from(bucket: "new_amazon")\
            |> range(start: {start_time}, stop: {end_time})\
            |> filter(fn: (r) => r["_measurement"] == "ecommerce_products")\
            |> filter(fn: (r) => r["_field"] == "actual_price")\
            |> filter(fn: (r) => r["asin"] == "{asin}")\
            |> filter(fn: (r) => r["user"] == "{user_name}")\
            |> yield(name: "mean")'
    elif product_name:
        query = f'from(bucket: "new_amazon")\
            |> range(start: {start_time}, stop: {end_time})\
            |> filter(fn: (r) => r["_measurement"] == "ecommerce_products")\
            |> filter(fn: (r) => r["_field"] == "actual_price")\
            |> filter(fn: (r) => r["product_name"] == "{product_name}")\
            |> filter(fn: (r) => r["user"] == "{user_name}")\
            |> yield(name: "mean")'
    else:
        query = f'from(bucket: "new_amazon")\
            |> range(start: {start_time}, stop: {end_time})\
            |> filter(fn: (r) => r["_measurement"] == "ecommerce_products")\
            |> filter(fn: (r) => r["_field"] == "actual_price")\
            |> filter(fn: (r) => r["user"] == "{user_name}")\
            |> yield(name: "mean")'
    # else:
    #     return JsonResponse({'error': 'No search parameter provided'}, status=400)     

    result = query_api.query(query=query,org='93eb79fe52548977')
    json_data = []
    for table in result:
        for record in table.records:
            record_dict = record.values
            json_data.append(record_dict)
    
    print("Result: {0}".format(json_data))
    return JsonResponse(data=json_data,safe=False)
    
def get_annual_data(request):
    asin = request.GET.get('asin')
    start_time, end_time = get_cookie_dates(request)
    user_name = request.session.get('username')

    query_api = influx_client.query_api()
    if asin not in ['','null']:
        query = 'from(bucket: "new_amazon")\
            |> range(start: {}, stop: {})\
            |> filter(fn: (r) => r["_measurement"] == "ecommerce_products")\
            |> filter(fn: (r) => r["_field"] == "actual_price")\
            |> filter(fn: (r) => r["asin"] == "{}")\
            |> filter(fn: (r) => r["user"] == "{}")\
            |> yield(name: "mean")'.format(start_time,end_time,asin,user_name)
    result = query_api.query(query=query,org='93eb79fe52548977')
    json_data = []
    for table in result:
            for record in table.records:
                timestamp = record.get_time()
                month_name = extract_month_name(timestamp)
                record_dict = {'month_name': month_name, **record.values}
                json_data.append(record_dict)

    print("Result: {0}".format(json_data))
    return JsonResponse(data=json_data, safe=False)

def extract_month_name(timestamp):
    dt_object = datetime.utcfromtimestamp(timestamp)
    month_name = dt_object.strftime('%B')
    return month_name

def get_data_view(request):
   asin = request.GET.get('asin')
   product_name = request.GET.get('product_name')
  
   if asin or product_name:
         influx_data = search_products(request)
         
   else:
        return JsonResponse({'error': 'No search parameter provided'}, status=400)
  
   if influx_data:
        # Process the data or return it as JsonResponse
        _time = []
        values = []
        # Assuming the structure of the returned data is in a suitable format for plotting
        for point in influx_data['results'][0]['series'][0]['values']:
            _time.append(point[0])  # Assuming timestamp is the first element
            values.append(point[1])  # Assuming the value is the second element

        return render(request, 'home.html', {
            'timestamps': _time,
            'values': values,
        })
   else:
       
       return JsonResponse({'error': 'Failed to fetch data from InfluxDB'}, status=500)
    
def handle_uploaded_file(uploaded_file):
    destination_directory = os.path.join(settings.BASE_DIR, 'csv_files')  # Adjust as needed

    # Ensure the destination directory exists; create if it doesn't
    os.makedirs(destination_directory, exist_ok=True)

    # Define the file path in the destination directory
    destination_file_path = os.path.join(destination_directory, uploaded_file.name)
    # Move the uploaded file to the destination directory
    with open(destination_file_path, 'wb') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return destination_file_path

    
def upload_to_influxdb(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        csv_file_path = handle_uploaded_file(uploaded_file)
        form = CSVUploadForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_csv = form.save(commit=False)
            uploaded_csv.user = request.user
            uploaded_csv.save()

        
        uploaded_file_instance = UploadedCSV(csv_file=uploaded_file, user=request.user)
        uploaded_file_instance.save()
        
        write_api = influx_client.write_api(write_options=SYNCHRONOUS)

        # Process CSV data and prepare for InfluxDB
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                _measurement = 'ecommerce_products'
                if row['_measurement'] != 'ecommerce_products':
                    row['_measurement'] = 'ecommerce_products'


                if '_measurement' not in row:
                    messages.warning(request, "Unsupported file: No measurement found.")
                    return redirect('/')
                  
                # Create a Point for each row in the CSV
                point = influxdb_client.Point(_measurement) \
                    .tag("asin", row['asin']) \
                    .tag("product_name", row['product_name']) \
                    .tag("category", row['category']) \
                    .tag("user",request.session.get('username')) \
                    .tag("files", uploaded_file_instance.id)\
                    .field(row['_field'], float(row['_value'])) \
                    .time(row['_time'], influxdb_client.WritePrecision.NS)
                    
              

                try:
                    # Write the point to the specified bucket
                    write_api.write(bucket=BUCKET_NAME, org=ORG_NAME, record=point)
                except Exception as e:
                    print(f"Failed to write: {e}")
                    messages.error(request,f"Exception occured with message: {str(e)} please review and re-upload the file")
                    return redirect('/')
        log_activity(request.user, "Uploaded a file")  # Log the activity     
        messages.success(request,"Your File is Successfully Uploaded!")
        return redirect('/')
            
    # return JsonResponse({'success':True, 'message':"Your File is Successfully Uploaded!"})
    return render('/templates/includes/navigation.html') 


#not-used
def delete_data_by_file(request):
    user_name = request.session.get('username')

    try:
        # Assuming 'file' is the name of the file input in your HTML form
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return JsonResponse(data={"status": "error", "message": "Invalid file"}, safe=False)

        # Use your handle_uploaded_file function to get the file name or path
        csv_file_path = handle_uploaded_file(uploaded_file)

        query_api = influx_client.query_api()

        # Construct delete query based on the file name
        delete_query = f'from(bucket: "new_amazon") \
                        |> filter(fn: (r) => r["_measurement"] == "ecommerce_products") \
                        |> filter(fn: (r) => r["user"] == "{user_name}" and r["files"] == "{uploaded_file.name}") \
                        |> delete()'

        # Execute the delete query
        result = query_api.query(query=delete_query, org='93eb79fe52548977')
        print("Delete Result: {0}".format(result))
        log_activity(request.user, "Deleted a file") 
        return JsonResponse(data={"status": "success"}, safe=False)

    except Exception as e:
        print(f"Failed to delete data: {e}")
    return JsonResponse(data={"status": "error", "message": str(e)}, safe=False)
    
def submitData(request):
    start_time, end_time = get_cookie_dates(request)
    if request.method == 'POST':
        try:
            # Retrieve necessary data from the form data
            decoded_body = request.body.decode('utf-8')
            if 'application/json' in request.content_type:
                json_data = json.loads(decoded_body)
                asin_values = json_data.get('asin')
                user_name = request.session.get('username')
                aggregator = json_data.get('stats')
                asin_condition = ' or '.join([f'r["asin"] == "{asin}"' for asin in asin_values])

                # Your InfluxDB query
                query_api = influx_client.query_api()
                query = f'from(bucket: "new_amazon")\
                    |> range(start: {start_time}, stop: {end_time})\
                    |> filter(fn: (r) => r["_measurement"] == "ecommerce_products")\
                    |> filter(fn: (r) => r["user"] == "{user_name}")\
                    |> filter(fn: (r) => {asin_condition})\
                    |> yield(name: "{aggregator}")'

                # Process the query here and execute it in InfluxDB
                result =  query_api.query(query=query,org='93eb79fe52548977')
                print(result)
                # Replace the following response with your actual response
                response = []
                for table in result:
                    for record in table.records:
                        record_dict = record.values
                        response.append(record_dict)
    
                print("Result: {0}".format(response))
                return JsonResponse(data=response,safe=False)
    
        except Exception as e:
            messages.error(request, f"Error in executing data: {e}")
            
    return redirect('/')


def time_upload_to_influx(request):
    if request.method == 'GET':
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')

        if not (start_time and end_time):
            messages.warning(request, "Please provide both start and end times.")
            return redirect('/')

    try:
        # Convert received strings to datetime objects
        # start_date_object = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        parsed_date = datetime.strptime(start_time, '%a %b %d %Y %H:%M:%S GMT%z')
        formatted_start_date = parsed_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                # formatted_start_date = start_date_object.strftime('%Y-%m-%dT%H:%M:%SZ')

        parsed_date = datetime.strptime(end_time, '%a %b %d %Y %H:%M:%S GMT%z')
        formatted_end_date = parsed_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        # end_date_object = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        # formatted_end_date = end_date_object.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        

        # query_api = influx_client.query_api()

        # # Replace '{{}}' with the actual ASIN value
        # query = f'from(bucket: "new_amazon")\
        #          |> range(start: {formatted_start_date}, stop: {formatted_end_date})\
        #          |> filter(fn: (r) => r["_measurement"] == "ecommerce_products")\
        #          |> filter(fn: (r) => r["_field"] == "actual_price")\
        #          |> yield(name: "mean")'

        # # Execute the InfluxDB query
        # result = query_api.query(query=query, org='93eb79fe52548977')
        # if len(result) == 0:
        #     messages.error(request, f"No data found in selected daterange.")
        #     return redirect('/')

            
        # j_response = []

        # for table in result:
        #     for record in table.records:
        #         record_dict = record.values
        #         j_response.append(record_dict)
        # response = JsonResponse(j_response,safe=False)
        
        response =  redirect('/')
        cookie_expiration = datetime.now() + timedelta(days=30)
        response.set_cookie('start_time',formatted_start_date,expires=cookie_expiration)
        response.set_cookie('end_time',formatted_end_date,expires=cookie_expiration)
        messages.success(request, "InfluxDB query executed successfully within the specified time range.")
        return response
    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, f"Error in executing InfluxDB query: {e}")

    return redirect('/')

def get_asin(request):
    asin = request.GET.get('asin')
    product_name = request.GET.get('product_name')
    user_name = request.session.get('username')
    start_time, end_time = get_cookie_dates(request)

    
    query_api = influx_client.query_api()
    if asin not in ['','null']:
        query = f'from(bucket: "new_amazon")\
            |> range(start: {start_time}, stop: {end_time})\
            |> filter(fn: (r) => r["_measurement"] == "ecommerce_products")\
            |> filter(fn: (r) => r["user"] == "{user_name}")\
            |> yield(name: "mean")'            
    result = query_api.query(query=query,org='93eb79fe52548977')
    json_data = []
    for table in result:
        for record in table.records:
            record_dict = record.values
            json_data.append(record_dict)
    
    print("Result: {0}".format(json_data))
    return JsonResponse(data=json_data,safe=False)
    
def get_all_category_sales_count(request):
    user_name = request.session.get('username')        
    query_api = influx_client.query_api()
    start_time, end_time = get_cookie_dates(request)

    query = f'from(bucket: "new_amazon")\
    |> range(start: {start_time}, stop: {end_time})\
    |> filter(fn: (r) => r["_measurement"] == "ecommerce_products")\
    |> filter(fn: (r) => r["user"] == "{user_name}")\
    |> filter(fn: (r) => r["_field"] == "sale_price")\
    |> group(columns: ["category"])\
    |> count()\
    |> yield(name: "count")'
    result = query_api.query(query=query,org='93eb79fe52548977')
    json_data = dict()
    for table in result:
            for record in table.records:
                record_dict = record.values
                cat = record_dict['category']
                json_data[record_dict['category']]  = record_dict['_value']
        
    print("Result: {0}".format(json_data))
    return JsonResponse(data=json_data,safe=False)
            


def get_all_category_data(request):
        user_name = request.session.get('username')  
        start_time, end_time = get_cookie_dates(request)
        query_api = influx_client.query_api()
        query = f'from(bucket: "new_amazon")\
        |> range(start: {start_time}, stop: {end_time})\
        |> filter(fn: (r) => r["_measurement"] == "ecommerce_products")\
        |> filter(fn: (r) => r["user"] == "{user_name}")\
        |> group(columns: ["category"])\
        |> last()\
        |> yield(name: "mean")'
                    
        result = query_api.query(query=query,org='93eb79fe52548977')
        json_data = []
        for table in result:
                for record in table.records:
                    record_dict = record.values
                    cat = record_dict['category']
                    json_data.append(cat)
            
        print("Result: {0}".format(json_data))
        return JsonResponse(data=json_data,safe=False)

def get_category_data_by_name(request):
    user_name = request.session.get('username')
    category = request.GET.get('category')
    start_time, end_time = get_cookie_dates(request)

    
    if request.method == 'POST':
        try:
                # Retrieve necessary data from the form data
                decoded_body = request.body.decode('utf-8')
                if 'application/json' in request.content_type:
                    json_data = json.loads(decoded_body)
                    selected_categories = json_data.get('selectedCategories')
        
                if not selected_categories:
                    return JsonResponse({'error': 'No category provided'}, status=400)


                query_api = influx_client.query_api()
                query = f'from(bucket: "new_amazon")\
                    |> range(start: {start_time}, stop: {end_time})\
                    |> filter(fn: (r) => r["_measurement"] == "ecommerce_products")\
                    |> filter(fn: (r) => r["_field"] == "actual_price")\
                    |> filter(fn: (r) => r["category"] =~ /{ "|".join(selected_categories) }/) \
                    |> filter(fn: (r) => r["user"] == "{user_name}")\
                    |> group(columns: ["category"])\
                    |> yield(name: "mean")'

                result = query_api.query(query=query, org='93eb79fe52548977')
                
                json_data = []
                for table in result:
                    for record in table.records:
                        record_dict = record.values
                        json_data.append(record_dict)
               
                print("Result: {0}".format(json_data))
                return JsonResponse(data=json_data, safe=False)
        except Exception as e:
                messages.error(request, f"Error in executing data: {e}")
                
def predict_sales_using_arima(request):
    user_name = request.session.get('username')
    category = request.GET.get('category')
    start_time, end_time = get_cookie_dates(request)

    
    
    # Retrieve necessary data from the form data
    decoded_body = request.body.decode('utf-8')
    if 'application/json' in request.content_type:
        json_data = json.loads(decoded_body)
        selected_categories = json_data.get('selectedCategories')

    if not selected_categories:
        return JsonResponse({'error': 'No category provided'}, status=400)


    query_api = influx_client.query_api()
    query = f'from(bucket: "new_amazon")\
        |> range(start: {start_time}, stop: {end_time})\
        |> filter(fn: (r) => r["_measurement"] == "ecommerce_products")\
        |> filter(fn: (r) => r["_field"] == "actual_price")\
        |> filter(fn: (r) => r["category"] =~ /{ "|".join(selected_categories) }/) \
        |> filter(fn: (r) => r["user"] == "{user_name}")\
        |> group(columns: ["category"])\
        |> yield(name: "mean")'

    result = query_api.query(query=query, org='93eb79fe52548977')
    
    json_data = []
    for table in result:
        for record in table.records:
            record_dict = record.values
            json_data.append(record_dict)
    
     #arima model code, should be separated from this function later.
    df = pd.DataFrame(json_data)
    df['_time'] = pd.to_datetime(df['_time'])
    # df.set_index('_time', inplace=True)
    time_series_data = df['_value']
    try:
        # aggregated_df = df.groupby('_time')['_value'].mean().reset_index()
        arima_model = auto_arima(time_series_data, seasonal=True)  # Assuming weekly seasonality
        forecast, conf_int = arima_model.predict(n_periods=7, return_conf_int=True)
    except Exception as e:
        pass
                    
    #forecast will contain the predicted values for the next 7 days
    #conf_int will contain the corresponding confidence intervals. 
    #The confidence intervals provide an indication of the uncertainty associated with each forecasted value. 
    #The narrower the interval, the more confident the model is in its prediction.
    
                           

