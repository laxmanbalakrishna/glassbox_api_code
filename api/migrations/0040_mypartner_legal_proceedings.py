# Generated by Django 4.1.7 on 2023-11-15 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0039_gstindetails"),
    ]

    operations = [
        migrations.AddField(
            model_name="mypartner",
            name="legal_proceedings",
            field=models.BooleanField(default=False),
        ),
    ]
