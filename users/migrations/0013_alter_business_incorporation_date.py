# Generated by Django 4.1.7 on 2023-04-06 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0012_alter_business_incorporation_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="business",
            name="incorporation_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
