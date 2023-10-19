# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from datetime import datetime
from influxdb_client import InfluxDBClient
from lib.ymlconfig import cfg

org = cfg("influxdb.org")
token = cfg("influxdb.token")
BUCKET = cfg("influxdb.bucket")
BUCKET_HOURLY = cfg("influxdb.bucket_hourly")
BANDWITH_MEASUREMENT = cfg("influxdb.bandwidth_measurement")
RESONSE_CODE_COUNT_MEASUREMENT = cfg("influxdb.response_code_measurement")
STATS_MEASUREMENT = cfg("influxdb.stats_measurement")
QA_MEASUREMENT = cfg("influxdb.qa_measurement")

url = cfg("influxdb.url")

client = InfluxDBClient(url=url, token=token)
