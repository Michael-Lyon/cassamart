from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("stores/", views.AllStoreListApiView.as_view(), name="store_list"),
    
    
    # Sellers Links
    path("seller/store-edit/<int:owner>/", views.StoreDetailUpdateView.as_view(), name="store_detail_update"),
    path("seller/category-detail-update/<int:pk>/",
         views.CategoryDetailUpdateApiView.as_view(), name="category_detail_update"),
    path("seller/product-detail-update/<int:pk>/",
         views.ProductDetailUpdateApiView.as_view(), name="product_detail_update"),
    
    path("seller/product/create/",
         views.ProductCreateApiView.as_view(), name="product_create"),
    
    path("seller/category/create/",
         views.CategoryCreateApiView.as_view(), name="category_create"),
    
    path("seller/my-order/", views.MyOrders.as_view(), name="my_orders"),
    
    #  Regular Links
    path("category-list/", views.CategoryListApiView.as_view(), name="category_list_create"),
    
    path("product-list/", views.ProductListApiView.as_view(), name="product_list_create"),
    
    path("cart/", views.CartView.as_view(), name="cart"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("goods-received/", views.GoodsReceived.as_view(), name="goods_recieved"),
    
]
