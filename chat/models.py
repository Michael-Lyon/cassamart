import random
import string

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

from accounts.models import Profile


def generate_ref_code():
    letters = string.ascii_lowercase
    code = ''.join(random.choice(letters) for i in range(12))
    return code


class Room(models.Model):
    name = models.CharField(max_length=1000, null=True, blank=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="buyer_rooms")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="seller_rooms")
    slug = models.SlugField(max_length=250, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(generate_ref_code())
        super(Room, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
    class Meta:
        verbose_name_plural = 'Rooms'
        ordering = ['-id']


class Messages(models.Model):
    message = models.CharField(max_length=100000)
    date = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.message} was sent by {self.sender.username} in room:{self.room.name}"

    class Meta:
        ordering = ['date']







# chat/serializers.py
# from rest_framework import serializers
# from .models import Room, Message

# class RoomSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Room
#         fields = '__all__'

# class MessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Message
#         fields = '__all__'