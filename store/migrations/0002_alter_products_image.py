# Generated by Django 4.1.7 on 2023-04-14 01:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="products",
            name="image",
            field=models.ImageField(upload_to="media/"),
        ),
    ]
