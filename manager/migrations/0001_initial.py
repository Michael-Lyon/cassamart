# Generated by Django 4.1.7 on 2024-10-09 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Configs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pcentage', models.DecimalField(decimal_places=2, default=0.01, max_digits=10)),
            ],
        ),
    ]
