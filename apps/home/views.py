# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import datetime, timedelta
import http
from http import client
import random
from django.conf import settings
from django.shortcuts import render
# import pandas as pd
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
from django.core.management.base import BaseCommand
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


def get_influx_data(request):
    # check_health = influx_client.health()
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    csv_file = 'amazon_final.csv'  # Replace with the path to your CSV file
    # # csv_file = request.params
    data_points = []
    fields = None  # Initialize fields as None

    # df = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vSSEhTtI2vxjkI0FmnWcQZjWSYvu2aCNe5JyMSi7-_XjQrvNCedPyORKPjIO2t58OwHRsFPJPvA8yNo/pubhtml?gid=1994285997&single=true')
    # # Iterate over rows in the DataFrame and write data to InfluxDB
    # # Iterate over rows in the DataFrame and write data to InfluxDB
    # for _, row in df.iterrows():
    #     # Convert timestamp to datetime
    #     timestamp = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
    #      # Use the field names from the first row
    #     data_point = {
    #         "measurement": "ecomm_data_new",
    #         "tags": {tag: row[tag] for tag in df.columns if tag != 'timestamp'},
    #         "time": timestamp,  # Change to the actual timestamp column name
    #         "fields": {}
    #     }

    #     # Iterate over columns in the DataFrame and add fields to the data point
    #     for col_name, col_value in row.items():
    #         # Convert column names to lowercase and replace spaces with underscores
    #         field_name = col_name.lower().replace(" ", "_")
            
    #         # Check if the column value is a valid number
    #         if pd.notna(col_value) and pd.to_numeric(col_value, errors="coerce") == col_value:
    #             data_point["fields"][field_name] = float(col_value)
    #         else:
    #             data_point["fields"][field_name] = str(col_value)

    #     try:
    #         # Write the data point to InfluxDB
    #         write_api.write(bucket=BUCKET_NAME, org=ORG_NAME, record=[data_point])
    #     except Exception as e:
    #         print(e)
    #         pass
            
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        # Read the first row to get the tag names
        tag_names = csv_reader.fieldnames
        # Read the first row to get field names
        fields = next(csv_reader)
        if '%' in fields['actual_price']:
            fields['actual_price'] = fields['actual_price'].replace("%",'')
            print(fields)
    
        for row in csv_reader:
            # Use the field names from the first row
            data_point = {
                "measurement": "ecomm_data_new",
                "tags": {tag: row[tag] for tag in tag_names},
                "time": row["timestamp"],  # Change to the actual timestamp column name
                "fields": {}
            }
            # data_point = {
            #     "measurement": "ecommerce_data",
            #     "tags": {
            #         "tag": 'amazon',  # Assuming the first column is a tag
            #     },
            #     "time": row["timestamp"],  # Assuming the third column is the timestamp
            #     "fields": {
            #         fields[0]: row[0],  # Use the first field name as a key
            #         fields[1]: row[1],    # Use the second field name as a key
            #         fields[2] : row[2],
            #         fields[3] : row[3],
            #         fields[4] : row[4],
                    
            #     }
        
            #}
            # Exclude tags from fields
            for field_name in row.keys():
                if field_name != "timestamp":
                    try:
                        field_value = row[field_name]
                        if field_name in ['discounted_price','actual_price','review']:
                            field_value = float(field_value.replace(",",''))
                        else:
                            data_point["fields"][field_name] = str(field_value)
                    except Exception as e:
                        print(e)
                        pass
                        # data_point["fields"][field_name] = str(row[field_name])

            #  # Use the field names from the first row
            # for i, field_name in enumerate(fields):
            #     if i > 0:  # Skip the first field (timestamp)
            #         data_point.field(field_name, row[i])

   
            try:
                write_api.write(bucket=BUCKET_NAME, org=ORG_NAME, record=[data_point])
            except Exception as e:
                print(e)
                pass
        #data_points.append(data_point)


        #Rest of your code remains the same for writing to InfluxDB

        # p = influxdb_client.Point("ecommerce_data").tag("amazon", "Prague").field("product_id", 1234)
        # write_api.write(bucket=BUCKET_NAME, org=ORG_NAME, record=p)
    return HttpResponse("check_ping")
   

def get_sample_influx_data(request):
    data = []
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    start_time = datetime(2023, 1, 1)  # Change the start date as needed
    sku_list = ['SKU001', 'SKU002', 'SKU003']  # List of sample SKUs
    item_names = ['Item A', 'Item B', 'Item C']  # List of sample item names
    for i in range(100):
        timestamp = start_time + timedelta(days=i)
        sku = random.choice(sku_list)
        item_name = item_names[sku_list.index(sku)]  # Match SKU to item name
        actual_price = random.uniform(10, 1000)  # Generating random prices
        data_point = {
            "measurement": "amazon_data",
            "time": timestamp.isoformat(),
            "fields": {
                "actual_price": actual_price,
                "sku": sku,
                "item_name": item_name
            }
        }
        write_api.write(bucket=BUCKET_NAME, org=ORG_NAME, record=[data_point])

        # data.append(data_point)
    return HttpResponse("check_ping 2")


def get_influx_product_id(request,product_id): 
    
    # query = 'select new_amazon from ecomm_data_new;'
    # # query_where = 'select new_amazon from ecomm_data_new where product_id=$product_id;'
    # query_where= 'SELECT * FROM "ecomm_data_new"'
    # bind_params = {'product_id': 'B07LDN9Q2P'}
    
    # print("Querying data: " + query_where)
    # result = client.query(query_where, bind_params=bind_params)
    # result = influxdb_client.Query(query=query_where)
    query_api = influx_client.query_api()
    query = 'from(bucket: "new_amazon")\
            |> range(start: 2015-06-23T06:50:11.897825+00:00, stop: 2023-06-23T06:50:11.897825+00:00)\
            |> filter(fn: (r) => r["_measurement"] == "ecomm_data_new")\
            |> filter(fn: (r) => r["_field"] == "product_id")\
            |> filter(fn: (r) => r["product_id"] == "B07LDN9Q2P")\
            |> count()\
            |> yield(name: "count")'

    result = query_api.query(query=query)
    print("Result: {0}".format(result))

    return HttpResponse(f"You're viewing product: {product_id}")


def get_data_view(request):
   influx_data = get_influx_product_id()
   if influx_data:
        # Process the data or return it as JsonResponse
        timestamps = []
        values = []
        # Assuming the structure of the returned data is in a suitable format for plotting
        for point in influx_data['results'][0]['series'][0]['values']:
            timestamps.append(point[0])  # Assuming timestamp is the first element
            values.append(point[1])  # Assuming the value is the second element

        return render(request, 'home.html', {
            'timestamps': timestamps,
            'values': values,
        })
   else:
        return JsonResponse({'error': 'Failed to fetch data from InfluxDB'}, status=500)



class Command(BaseCommand):
    help = 'Convert quoted string values to numerical data types'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str, help='Input CSV file')
        parser.add_argument('output_file', type=str, help='Output CSV file')

    def handle(self, *args, **options):
        input_file = options['input_file']
        output_file = options['output_file']

        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames

            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                # Convert quoted strings to numbers where applicable
                for row[2] in fieldnames:
                    if row[2].strip().isdigit():
                        row[2] = int(row[2])
                    else:
                        try:
                            row[2] = float(row[2])
                        except (ValueError, TypeError):
                            pass

                writer.writerow(row)

        self.stdout.write(self.style.SUCCESS(f'Conversion complete. Saved to {output_file}'))

