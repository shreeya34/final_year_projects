# Generated by Django 4.2.8 on 2023-12-14 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email',
            field=models.EmailField(default='example@example.com', max_length=254),
        ),
    ]
