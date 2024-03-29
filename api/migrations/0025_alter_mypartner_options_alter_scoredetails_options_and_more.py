# Generated by Django 4.1.7 on 2023-05-09 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0024_alter_mypartner_options_scoredetails"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="mypartner",
            options={"ordering": ("-updated_on",)},
        ),
        migrations.AlterModelOptions(
            name="scoredetails",
            options={"ordering": ("-updated_on",)},
        ),
        migrations.AlterField(
            model_name="mypartner",
            name="updated_on",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
