from django.urls import path
from . import views


app_name = "store"

urlpatterns = [
    path("stores/", views.AllStoreListApiView.as_view(), name="store_list"),
    
    # Sellers Links
    path("seller/store-edit/<int:store>/", views.StoreDetailUpdateView.as_view(), name="store_detail_update"),
    path("seller/category-detail-update/<int:pk>/",
         views.CategoryDetailUpdateApiView.as_view(), name="category_detail_update"),
    path("seller/product-detail-update/<int:pk>/",
         views.ProductDetailUpdateApiView.as_view(), name="product_detail_update"),
    
    
    #  Regular Links
    path("category-list-create/", views.CategoryListCreateApiView.as_view(), name="category_list_create"),
    
    path("product-list-create/", views.ProductListCreateApiView.as_view(), name="product_list_create"),
]
