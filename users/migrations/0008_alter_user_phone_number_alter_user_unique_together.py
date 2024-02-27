# Generated by Django 4.1.7 on 2023-04-04 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_user_country_user_state_alter_user_city"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name="user",
            unique_together={("phone_number", "pan_number", "email")},
        ),
    ]
