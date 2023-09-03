# Generated by Django 4.1.7 on 2023-04-28 07:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0003_buyerprofile_address"),
    ]

    operations = [
        migrations.AlterField(
            model_name="buyerprofile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="buyer",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="sellerprofile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="seller",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
