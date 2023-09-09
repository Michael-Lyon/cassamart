from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
     path("stores/", views.StoreListApiView.as_view(), name="store_list"),
     path("stores/<int:store_id>/", views.StoreDetailApiView.as_view(), name="store_detail"),

     # Sellers Links
     # path("seller/store-edit/<int:owner>/", views.StoreDetailUpdateView.as_view(), name="store_detail_update"),

     path("seller/product-detail-update/<int:pk>/", views.ProductDetailUpdateApiView.as_view(), name="product_detail_update"),


     path("seller/product/create/", views.ProductCreateApiView.as_view(), name="product_create"),

     path("seller/my-order/", views.MyOrders.as_view(), name="my_orders"),

     #  Regular Links
     path("categories/", views.CategoryList.as_view(), name="category_list"),

     path("categories/<int:category_id>/", views.CategoryDetail.as_view(), name="category_detail"),

     path("products/", views.ProductListApiView.as_view(), name="product_list"),

     path("cart/", views.CartView.as_view(), name="cart"),
     path("checkout/", views.CheckoutView.as_view(), name="checkout"),

     path("goods-received/", views.GoodsReceived.as_view(), name="goods_recieved"),

]


