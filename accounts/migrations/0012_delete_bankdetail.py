# Generated by Django 4.1.7 on 2024-05-11 14:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0002_bankdetail_alter_transaction_bank_details"),
        ("accounts", "0011_bankdetail_delete_bankdetails"),
    ]

    operations = [
        migrations.DeleteModel(
            name="BankDetail",
        ),
    ]
