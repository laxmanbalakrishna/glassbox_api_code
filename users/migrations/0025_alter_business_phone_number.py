# Generated by Django 4.1.7 on 2023-05-01 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0024_business_district_alter_business_country"),
    ]

    operations = [
        migrations.AlterField(
            model_name="business",
            name="phone_number",
            field=models.CharField(blank=True, default="", max_length=15, null=True),
        ),
    ]
