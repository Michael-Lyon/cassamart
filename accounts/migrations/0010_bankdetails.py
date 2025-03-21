# Generated by Django 4.1.7 on 2024-04-24 14:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0009_remove_profile_nin_address_is_default_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BankDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("account_number", models.CharField(max_length=100)),
                ("bank_code", models.CharField(max_length=10)),
                (
                    "recipient_code",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
