
from django.core.mail import send_mail

from django.conf import settings 


def send_forget_password_mail(email , token ):
    subject = 'Your forget password link'
    message = f'Hi , click on the link to reset your password http://127.0.0.1:8000/change-password/{token}/'
    email_from = settings.EMAIL_HOST_USER
    auth_user=settings.EMAIL_HOST_USER
    auth_password=settings.EMAIL_HOST_PASSWORD
    recipient_list = [email]
    send_mail(subject=subject, message=message, from_email=email_from, recipient_list=recipient_list,auth_password=auth_password,auth_user=auth_user)
    return True
    
