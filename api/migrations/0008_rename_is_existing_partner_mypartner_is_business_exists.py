# Generated by Django 4.1.7 on 2023-04-13 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0007_mypartner_is_existing_partner"),
    ]

    operations = [
        migrations.RenameField(
            model_name="mypartner",
            old_name="is_existing_partner",
            new_name="is_business_exists",
        ),
    ]
