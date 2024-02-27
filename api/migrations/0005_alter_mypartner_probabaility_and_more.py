# Generated by Django 4.1.7 on 2023-04-13 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0004_alter_mypartner_probabaility_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mypartner",
            name="Probabaility",
            field=models.CharField(
                choices=[
                    (0, "0%"),
                    (1, "25%"),
                    (2, "50%"),
                    (3, "75%"),
                    (4, "90%"),
                    (5, "100%"),
                ],
                default=0,
                max_length=80,
            ),
        ),
        migrations.AlterField(
            model_name="mypartner",
            name="on_time_Payment",
            field=models.CharField(
                choices=[
                    (0, "0%"),
                    (1, "25%"),
                    (2, "50%"),
                    (3, "75%"),
                    (4, "90%"),
                    (5, "100%"),
                ],
                default=0,
                max_length=80,
            ),
        ),
    ]