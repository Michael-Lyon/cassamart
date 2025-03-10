from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("forgot-password/", views.reset_password_view, name="forgot_password"),

    path("my-profile/", views.ProfileView.as_view(), name="profile"),

    path("my-profile-fcm-token/", views.FCMUpdateView.as_view(), name="profile_fcm"),

    path("register/seller/", views.SellerCreateView.as_view(), name="seller_register"),

    path("register/buyer/", views.BuyerCreateView.as_view(), name="buyer_register"),

    path('seller-profile/', views.SellerProfileUpdateView.as_view(), name='seller-profile-update'),
    path('buyer-profile/', views.BuyerProfileUpdateView.as_view(), name='buyer-profile-update'),


    path('become-buyer/', views.BecomeBuyer.as_view(), name='become_buyer'),
    path('become-seller/', views.BecomeSeller.as_view(), name='become_seller'),

    path("change-password/", views.ChangePasswordView.as_view(), name="change_password"),

    path('addresses/', views.AddressListCreateView.as_view(),
        name='address-list-create'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address-detail'),


]

