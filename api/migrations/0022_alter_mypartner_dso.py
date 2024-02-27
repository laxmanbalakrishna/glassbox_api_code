# Generated by Django 4.1.7 on 2023-05-01 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0021_alter_mypartner_updated_on"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mypartner",
            name="dso",
            field=models.IntegerField(
                choices=[
                    (0, "0 Days"),
                    (0, ">60 Days"),
                    (1, ">90 Days"),
                    (2, ">120 Days"),
                    (3, ">150 Days"),
                    (4, ">180 Days"),
                    (5, ">360 Days"),
                ],
                default=0,
            ),
        ),
    ]
