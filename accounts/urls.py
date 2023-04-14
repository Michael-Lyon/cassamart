from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/seller/", views.SellerCreateView.as_view(), name="seller_register"),
    
    path("register/buyer/", views.BuyerCreateView.as_view(), name="buyer_register"),

    path("change-password/", views.ChangePasswordView.as_view(), name="change_password"),
    
    
]

