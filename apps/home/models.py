# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
from django import forms
from core.influx import influx_client



def get_product_info(self, product_id):
    query = """
        from(bucket: "amazon_new")
        |> range(start: 0)
        |> filter(fn: (r) => r["_measurement"] == "{}" and r["_field"] == "product_id" and r["_value"] == "{}")
    """.format("ecoome_data_new",product_id)
    
    influx_query = influx_client.query_client(query)
    return influx_query

    
    
    

