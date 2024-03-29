# Generated by Django 4.1.7 on 2023-04-06 09:47

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0010_alter_user_business_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="business_name",
        ),
        migrations.RemoveField(
            model_name="user",
            name="cin",
        ),
        migrations.RemoveField(
            model_name="user",
            name="city",
        ),
        migrations.RemoveField(
            model_name="user",
            name="company",
        ),
        migrations.RemoveField(
            model_name="user",
            name="country",
        ),
        migrations.RemoveField(
            model_name="user",
            name="industry",
        ),
        migrations.RemoveField(
            model_name="user",
            name="owner_name",
        ),
        migrations.RemoveField(
            model_name="user",
            name="state",
        ),
        migrations.AlterField(
            model_name="user",
            name="pan_number",
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
        migrations.CreateModel(
            name="Business",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, default="", max_length=200, null=True
                    ),
                ),
                ("pan_number", models.CharField(max_length=10, unique=True)),
                (
                    "incorporation_date",
                    models.DateTimeField(
                        blank=True, default=datetime.date.today, null=True
                    ),
                ),
                ("name", models.CharField(max_length=80)),
                (
                    "city",
                    models.CharField(blank=True, default="", max_length=100, null=True),
                ),
                (
                    "state",
                    models.CharField(blank=True, default="", max_length=100, null=True),
                ),
                (
                    "country",
                    models.CharField(blank=True, default="", max_length=100, null=True),
                ),
                ("cin", models.CharField(blank=True, max_length=100, null=True)),
                ("phone_number", models.CharField(default="", max_length=15)),
                (
                    "company",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.companytype",
                    ),
                ),
                (
                    "industry",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.industry",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="business",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="users.business",
            ),
        ),
    ]
