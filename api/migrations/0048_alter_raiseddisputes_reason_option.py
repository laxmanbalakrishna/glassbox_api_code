# Generated by Django 4.1.7 on 2024-02-27 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0047_alter_notification_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="raiseddisputes",
            name="reason_option",
            field=models.CharField(
                blank=True,
                choices=[
                    ("NOT_HAVING_ANY_TRANS", "I am not having any transaction"),
                    ("HAVE_PENDING_CREDIT_NOTES", "I have pending credit notes"),
                    ("ALREADY_MADE_THE_PAYMENT", "I already made the payment"),
                    ("OTHERS", "Others"),
                ],
                max_length=100,
                null=True,
            ),
        ),
    ]
