import json
from django.db import transaction

from python_paystack.managers import TransactionsManager
from .serializers import CartSerializer, CartItemSerializer
from .models import Cart, CartItem
from rest_framework import status as stat
from rest_framework.views import APIView
from rest_framework import generics, mixins
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from .models import Product, Store, Category, Checkout
from .serializers import AllStoreDetailSerializer, StoreSerializer, CategorySerializer, ProductSerializer, CheckoutSerializer, TicketSerializer
from . import utils

from accounts.models import Wallet

class AllStoreListApiView(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = AllStoreDetailSerializer


class CategoryListApiView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryCreateApiView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailUpdateApiView(generics.RetrieveUpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "pk"


class ProductListApiView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductCreateApiView(generics.CreateAPIView):
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


class CartView(APIView):
    """
    Endpoint: `/api/cart/`

        HTTP Methods:
        - GET: Retrieve the user's cart.
        - POST: Add an item to the cart.
        - PUT: Update the quantity of items in the cart.
        - DELETE: Remove items from the cart.

        Request and Response Details:

        1. GET Request:
        - Method: GET
        - URL: `/api/cart/`
        - Headers: Authorization token (JWT)
        - Response:
            - 200 OK: Returns the serialized data of the user's cart.
            - 404 Not Found: If the cart does not exist for the user.

        2. POST Request:
        - Method: POST
        - URL: `/api/cart/`
        - Headers: Authorization token (JWT)
        - Body: JSON object containing the following fields:
            - `product`: ID of the product to add to the cart.
            - `quantity`: Quantity of the product to add.
        - Response:
            - 201 Created: Returns the serialized data of the added cart item.
            - 400 Bad Request: If the request data is invalid.

        3. PUT Request:
        - Method: PUT
        - URL: `/api/cart/`
        - Headers: Authorization token (JWT)
        - Body: JSON array containing objects with the following fields:
            - `product`: ID of the product to update.
            - `quantity`: New quantity of the product.
        - Response:
            - 200 OK: Indicates a successful update of the cart items.
            - 404 Not Found: If the cart or any cart item does not exist.

        4. DELETE Request:
        - Method: DELETE
        - URL: `/api/cart/`
        - Headers: Authorization token (JWT)
        - Body: JSON array containing objects with the following fields:
            - `product`: ID of the product to remove from the cart.
        - Response:
            - 204 No Content: Indicates successful removal of the cart items.
            - 404 Not Found: If the cart or any cart item does not exist.

        Note: Make sure to include the necessary authentication token (JWT) in the request headers for all endpoints to authenticate the user.

    """
    
    def get(self, request):
        user = request.user
        print(user)
        try:
            cart = Cart.objects.filter(user=user)
            serializer = CartSerializer(cart, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            print(e)
            return Response(status=stat.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        data = request.data

        try:
            cart = Cart.objects.get(user=user, paid=False)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=user)
        
        data["cart"] = cart.id
        serializer = CartItemSerializer(data=data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            try:
                cart_item = CartItem.objects.get(cart=cart, product=product)
                cart_item.quantity += quantity
                cart_item.save()
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            serializer.save()
            return Response(serializer.data, status=stat.HTTP_201_CREATED)
        return Response(serializer.errors, status=stat.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user
        data = request.data
        cart = Cart.objects.get(user=user, paid=False)
        for item_data in data:
            product_id = item_data['product']
            quantity = item_data['quantity']
            try:
                cart_item = CartItem.objects.get(cart=cart, product__id=product_id)
                cart_item.quantity = quantity
                cart_item.save()
            except Cart.DoesNotExist:
                return Response(status=stat.HTTP_404_NOT_FOUND)

        return Response(status=stat.HTTP_200_OK)

    def delete(self, request):
        user = request.user
        data = request.data

        try:
            cart = Cart.objects.get(user=user, paid=False)
            for item_data in data:
                cart_item = CartItem.objects.get(cart=cart, product__id=item_data['product'])
                cart_item.delete()
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(status=stat.HTTP_404_NOT_FOUND)

        return Response(status=stat.HTTP_204_NO_CONTENT)


class CheckoutView(APIView):
    
    def get(self, request):
        user = request.user
        cart = Cart.objects.get(user=user, paid=False)

        # Calculate the total amount based on cart items
        products = CartItem.objects.filter(cart=cart)
        total_amount = sum(item.product.price * item.quantity for item in products)
        serializer = CartSerializer(cart, context={'request': request})
        data = serializer.data
        data["total_amount"] = total_amount
        return Response(data, status=stat.HTTP_200_OK)
        
    
    def post(self, request):
        user = request.user
        cart = Cart.objects.get(user=user, paid=False)
        data = request.data
        
        # Calculate the total amount based on cart items
        total_amount = data["total_amount"]
        reference = data["reference"]
        delivery_address = data["delivery_address"]
        
        status = utils.check_payment(reference)
        if status == 'success':
            checkout = Checkout.objects.get_or_create(user=user, cart=cart, total_amount=total_amount, status='paid', delivery_address=delivery_address, payment_status=True)
            cart.paid = True
            cart.save()
            # send mails to the oowners of the goods that they have a new order
            utils.send_order_mail(cart)
            
            serializer = CheckoutSerializer(checkout)
            return Response(serializer.data, status=stat.HTTP_201_CREATED)
        else:
            return Response({"message": "Failed Transaction try again"}, status=stat.HTTP_402_PAYMENT_REQUIRED)




class GoodsReceived(APIView):
    def post(self, request):
        data = request.data
        user = request.user
        owners = {}
        id = data["id"]
        cart = Cart.objects.get(id=id, user=user)
        status = data['status']
        if status:
            for cart_item in cart.cartitem_set.all():
                product_owner = cart_item.product.category.store.owner
                payment_amount = cart_item.product.price * cart_item.quantity
                
                owners.setdefault(product_owner, 0)
                owners[product_owner]+= payment_amount
                # Add each product owner money to thier wallet
                created, wallet = Wallet.objects.get_or_create(user=product_owner)
                wallet.amount += payment_amount
            # send mails to the onwers of the products that their accounts have been topped
            utils.send_wallet_mail(owners)
            return Response({"message":"Updated."} , status=stat.HTTP_200_OK)
        return Response({"message":"Updated."} , status=stat.HTTP_409_CONFLICT)
        

class MyOrders(APIView):
    def get(self, request):
        store = request.user.my_store
        checkouts = Checkout.objects.filter(cart__items__category__store=store)
        serializer = CheckoutSerializer(checkouts, many=True)
        return Response(serializer.data, status=stat.HTTP_200_OK)
