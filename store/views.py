from rest_framework import generics, mixins
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from .models import Product, Store, Category
from .serializers import AllStoreDetailSerializer, StoreSerializer, CategorySerializer, ProductSerializer


class AllStoreListApiView(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = AllStoreDetailSerializer


class CategoryListCreateApiView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailUpdateApiView(generics.RetrieveUpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "pk"

class ProductListCreateApiView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailUpdateApiView(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "pk"


class StoreDetailUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    lookup_field = "owner"