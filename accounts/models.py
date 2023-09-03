from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
User = get_user_model()

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="sellerprofile")
    nin = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    # identity_document = models.FileField(upload_to="identity_document/%Y/%m/%d/")
    # TODO ADD A PROPER STR FOR THESE MODELS


class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="buyerprofile")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)




class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    amount = models.DecimalField(max_digits=200, decimal_places=2, default=0.0)
