from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),

    path("profile/seller/", views.ProfileView.as_view(), name="profile"),

    path("register/seller/", views.SellerCreateView.as_view(), name="seller_register"),

    path("register/buyer/", views.BuyerCreateView.as_view(), name="buyer_register"),

    path('seller-profile/', views.SellerProfileUpdateView.as_view(), name='seller-profile-update'),
    path('buyer-profile/', views.BuyerProfileUpdateView.as_view(), name='buyer-profile-update'),

    path("change-password/", views.ChangePasswordView.as_view(), name="change_password"),

]

