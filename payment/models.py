from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


class BankDetail(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bank_details")
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=10)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    recipient_code = models.CharField(max_length=100, null=True, blank=True)



class Transaction(models.Model):
    bank_details = models.ForeignKey(BankDetail, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    transfer_code = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

