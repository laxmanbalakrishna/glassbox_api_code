# Generated by Django 4.1.7 on 2023-04-27 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0014_alter_mypartner_dso"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mypartner",
            name="dso",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (0, ">60 Days"),
                    (1, ">90 Days"),
                    (2, ">120 Days"),
                    (3, ">150 Days"),
                    (4, ">180 Days"),
                ],
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="mypartner",
            name="score",
            field=models.IntegerField(
                choices=[
                    (1, "Excellent"),
                    (2, "Good"),
                    (3, "Delay payment"),
                    (4, "Defaulter"),
                    (5, "Intentional Fraud"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="mypartner",
            name="total_outstanding",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (0, "<5 Lakh"),
                    (1, "10-20 Lakh"),
                    (2, "20-50 Lakh"),
                    (3, "50L-1 Cr"),
                    (4, ">1 Cr"),
                ],
                null=True,
            ),
        ),
    ]
