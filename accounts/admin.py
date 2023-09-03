from django.contrib import admin

from .models import BuyerProfile, SellerProfile

admin.site.register(BuyerProfile)
admin.site.register(SellerProfile)