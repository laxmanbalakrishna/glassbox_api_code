# Generated by Django 4.1.7 on 2023-04-06 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0011_remove_user_business_name_remove_user_cin_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="business",
            name="incorporation_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
