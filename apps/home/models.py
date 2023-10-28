# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
from django import forms
from .models import get_influx_data

# Create your models here.
class get_influx_data(forms.ModelForm):
    class Meta:
        model = get_influx_data
        fields = '__all__'  # or specify the fields you want to include

    def clean_field_name(self):
        data = self.cleaned_data['field_name']
        # Implement data cleaning/validation logic for the field
        # Example: Remove leading and trailing whitespace
        cleaned_data = data.strip()
        return cleaned_data

