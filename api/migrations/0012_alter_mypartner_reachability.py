# Generated by Django 4.1.7 on 2023-04-19 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0011_alter_mypartner_on_time_payment_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mypartner",
            name="reachability",
            field=models.IntegerField(
                choices=[(1, "Yes"), (2, "Difficult"), (0, "No")], default=0
            ),
        ),
    ]
