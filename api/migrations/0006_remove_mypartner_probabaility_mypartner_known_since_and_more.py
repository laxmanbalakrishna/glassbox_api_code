# Generated by Django 4.1.7 on 2023-04-13 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_alter_mypartner_probabaility_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mypartner",
            name="Probabaility",
        ),
        migrations.AddField(
            model_name="mypartner",
            name="known_since",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="mypartner",
            name="recovery_probability",
            field=models.CharField(
                choices=[(0, "Yes"), (1, "Difficult"), (2, "No")],
                default=0,
                max_length=80,
            ),
        ),
        migrations.AlterField(
            model_name="mypartner",
            name="dso",
            field=models.CharField(default="", max_length=200),
        ),
        migrations.AlterField(
            model_name="mypartner",
            name="reachability",
            field=models.CharField(
                choices=[(0, "Yes"), (1, "Difficult"), (2, "No")],
                default=0,
                max_length=255,
            ),
        ),
    ]
