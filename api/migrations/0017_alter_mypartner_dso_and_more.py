# Generated by Django 4.1.7 on 2023-04-27 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0016_alter_mypartner_dso_and_more"),
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
                ],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="mypartner",
            name="total_outstanding",
            field=models.IntegerField(
                choices=[
                    (0, "0"),
                    (1, "<5 Lakh"),
                    (2, "10-20 Lakh"),
                    (3, "20-50 Lakh"),
                    (4, "50L-1 Cr"),
                    (5, ">1 Cr"),
                ],
                default=0,
            ),
        ),
    ]
