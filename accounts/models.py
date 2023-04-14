from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nin = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)


class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
