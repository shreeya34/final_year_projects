from django.conf import settings
# from influxdb import client
import influxdb_client

# Create the InfluxDB client

host = settings.INFLUXDB_SETTINGS['host']
port=settings.INFLUXDB_SETTINGS['port']
# username = settings.INFLUXDB_SETTINGS['username']
# password = settings.INFLUXDB_SETTINGS['password']
token = settings.INFLUXDB_SETTINGS['token']
org = settings.INFLUXDB_SETTINGS['org']

url = "http://{}:{}".format(host,port)
influx_client = influxdb_client.InfluxDBClient(url=url,token=token,org=org)