from . import views
from django.urls import path, re_path

app_name= "payment"

urlpatterns = [

    path("banks/list/", views.GetBanksView.as_view(), name="get_banks"),

    path("banks/list/", views.GetBanksView.as_view(), name="get_banks"),

    path("goods-received/", views.GoodsReceived.as_view(), name="goods_recieved"),

    path("bank-details/", views.BankDetailView.as_view(), name='bank_details'),

    path("bank/resolve/", views.AccountNumberResolver.as_view(), name='account_resolve'),
]

