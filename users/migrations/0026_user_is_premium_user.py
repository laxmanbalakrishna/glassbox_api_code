# Generated by Django 4.1.7 on 2023-08-07 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0025_alter_business_phone_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_premium_user",
            field=models.BooleanField(default=False),
        ),
    ]