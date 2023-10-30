# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.conf import settings
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from core.influx import influx_client
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from django.conf import settings
import csv
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

    csv_file = './amazon.csv'  # Replace with the path to your CSV file
    csv_file = request.params
    data_points = []
    fields = None  # Initialize fields as None

    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)

        # Read the first row to get field names
        fields = next(csv_reader)

        for row in csv_reader:
            # Use the field names from the first row
            data_point = {
                "measurement": "ecommerce_data",
                "tags": {
                    "tag": 'amazon',  # Assuming the first column is a tag
                },
                # "time": row[2],  # Assuming the third column is the timestamp
                "fields": {
                    fields[0]: row[0],  # Use the first field name as a key
                    fields[1]: row[1],    # Use the second field name as a key
                    fields[2] : row[2],
                    fields[3] : row[3],
                    fields[4] : row[4],
                    
                }
        
            }
             # Use the field names from the first row
        for i, field_name in enumerate(fields):
                if i > 0:  # Skip the first field (timestamp)
                    data_point.field(field_name, row[i])

   
            
        write_api.write(bucket=BUCKET_NAME, org=ORG_NAME, record=data_point)
        data_points.append(data_point)


        # Rest of your code remains the same for writing to InfluxDB

        # p = influxdb_client.Point("ecommerce_data").tag("amazon", "Prague").field("product_id", 1234)
        # write_api.write(bucket=BUCKET_NAME, org=ORG_NAME, record=p)
        return HttpResponse("check_ping")
    


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

