# Generated by Django 4.1.7 on 2023-09-14 05:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0034_mypartner_capital_mypartner_transaction_paid_ontime"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Notification",
        ),
    ]
