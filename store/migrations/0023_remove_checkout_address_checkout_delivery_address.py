# Generated by Django 4.1.7 on 2023-12-29 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0022_remove_checkout_delivery_address_checkout_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkout',
            name='address',
        ),
        migrations.AddField(
            model_name='checkout',
            name='delivery_address',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
