# Generated by Django 4.1.7 on 2023-11-10 05:02

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0037_alter_mypartner_score_payments"),
    ]

    operations = [

        migrations.AddField(
            model_name="mypartner",
            name="assets",
            field=models.IntegerField(
                choices=[(1, "Yes"), (2, "No"), (0, "Average")], default=0
            ),
        ),
        migrations.AlterField(
            model_name="mypartner",
            name="capital",
            field=models.IntegerField(
                choices=[(1, "Yes"), (2, "No"), (0, "Average")], default=0
            ),
        ),
        migrations.AlterField(
            model_name="mypartner",
            name="score",
            field=models.IntegerField(
                choices=[
                    (10, "Excellent"),
                    (9, "Good"),
                    (8, "Average"),
                    (7, "Service Delay"),
                    (6, "Lack of Post-Sale Support"),
                    (5, "Market Disruption/Dispute/UnderCutting\t"),
                    (4, "Payment Delay"),
                    (3, "Non-Delivery After Payment"),
                    (2, "Payment Defaul"),
                    (1, "Fraudulent Activity"),
                ]
            ),
        ),
    ]
