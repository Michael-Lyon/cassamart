# Generated by Django 4.1.7 on 2023-06-02 00:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0007_checkout_reference"),
    ]

    operations = [
        migrations.AddField(
            model_name="checkout",
            name="delivery_address",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
