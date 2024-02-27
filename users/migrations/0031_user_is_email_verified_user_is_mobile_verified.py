# Generated by Django 4.2.5 on 2024-02-20 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_business_is_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_mobile_verified',
            field=models.BooleanField(default=False),
        ),
    ]
