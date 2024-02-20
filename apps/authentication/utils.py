from .models import ActivityLog

# forms.py
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

def log_activity(user, action):
    ActivityLog.objects.create(user=user, action=action)