
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db import models, transaction

from accounts.utils import get_code

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

    def save(self, *args, **kwargs):
        if self.is_default:
            with transaction.atomic():
                # Set all other addresses for this user to not default
                Address.objects.filter(
                    user=self.user, is_default=True).update(is_default=False)
        super(Address, self).save(*args, **kwargs)


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    amount = models.DecimalField(max_digits=200, decimal_places=2, default=0.0)

# MODELS TO STORE AUTHENTICTAION CODES


class UserAuthExpiredManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(expires_at__lte=timezone.now())

class MyUserAuth(models.Model):
    user = models.OneToOneField(
        User, related_name="user_auth_code", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now)
    code = models.CharField(max_length=10, default="123456")
    expired = UserAuthExpiredManager()
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = get_code()
        self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user} ({self.code})"
