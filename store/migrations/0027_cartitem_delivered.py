# Generated by Django 4.1.7 on 2024-06-06 05:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0026_cartitem_received"),
    ]

    operations = [
        migrations.AddField(
            model_name="cartitem",
            name="delivered",
            field=models.BooleanField(default=False),
        ),
    ]