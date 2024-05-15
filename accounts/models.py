from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    is_buyer = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    fcm_token = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.address


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    amount = models.DecimalField(max_digits=200, decimal_places=2, default=0.0)




