from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
     path("stores/", views.StoreListApiView.as_view(), name="store_list"),
     path("stores/<int:pk>/", views.StoreDetailApiView.as_view(), name="store_detail"),

     # Sellers Links
     path("stores/<int:id>/update/", views.StoreDetailUpdateView.as_view(), name="store_detail_update"),

     path("seller/product-detail-update/<int:pk>/", views.ProductDetailUpdateApiView.as_view(), name="product_detail_update"),


     path("seller/product/create/", views.ProductCreateApiView.as_view(), name="product_create"),

     path("seller/my-order/", views.MyOrders.as_view(), name="my_orders"),
     path("seller/my-store/", views.MyStore.as_view(), name="my_store"),
     path("seller/goods-delivered/", views.GoodsDelivered.as_view(), name="goods_delivered"),

     #  Regular Links
     path("my-orders/", views.BuyerOrders.as_view(), name="buyer_orders"),

     path("categories/", views.CategoryList.as_view(), name="category_list"),

     path("send-message-notification/",
          views.SendMessageNotificationView.as_view(), name="send_message_notification"),

     path("categories/<int:pk>/", views.CategoryDetail.as_view(), name="category_detail"),

     path("products/", views.ProductListApiView.as_view(), name="product_list"),
     path("products/<int:pk>/",
          views.ProductDetailApiView.as_view(), name="product_detail"),

     path("products/delete/<int:pk>/",
          views.ProductDeleteApiView.as_view(), name="product_delete"),

     path("cart/", views.CartView.as_view(), name="cart"),
     path("checkout/", views.CheckoutView.as_view(), name="checkout"),
     path("checkout/cancel/", views.CancelCheckout.as_view(), name="cancel_checkout"),

     path('wishlist/', views.WishlistItemCreateView.as_view(), name='wishlist-create'),
     path('wishlist/list/', views.WishlistItemListView.as_view(), name='wishlist-list'),
     path('wishlist/delete/<int:pk>/', views.WishlistItemDeleteView.as_view(), name='wishlist-delete'),

     # CHART DATA
     path('chart/<int:store_id>/', views.SalesDataView.as_view(), name='sales-data'),
]



