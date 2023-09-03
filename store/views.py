import json

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import generics, mixins
from rest_framework import status
from rest_framework import status as stat
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import Wallet
from python_paystack.managers import TransactionsManager

from . import utils
from .models import (Cart, CartItem, Category, Checkout, Discount, Product, Store)
from .serializers import (AllStoreDetailSerializer, CartItemSerializer,
                          CartSerializer, CategorySerializer,
                          CheckoutSerializer, ProductSerializer,
                          StoreSerializer, TicketSerializer)
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()



class AllStoreListApiView(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = AllStoreDetailSerializer
    
    @swagger_auto_schema(
        operation_description="Retrieve a list of all stores.",
        responses={200: AllStoreDetailSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CategoryListApiView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    @swagger_auto_schema(
        operation_description="Retrieve a list of all categories.",
        responses={200: CategorySerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CategoryCreateApiView(generics.CreateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    # @swagger_auto_schema(
    #     operation_description="Create a new category.",
    #     request_body=CategorySerializer,  # Specify the request body serializer
    #     responses={201: CategorySerializer},  # Specify the expected response
    # )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CategoryDetailUpdateApiView(generics.RetrieveUpdateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "pk"

    @swagger_auto_schema(
        operation_description="Retrieve or update a category by ID.",
        responses={200: CategorySerializer()},  # Specify the expected response for retrieval
        # request_body=CategorySerializer(),  # Specify the request body serializer for updating
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a category by ID.",
        responses={200: CategorySerializer()},  # Specify the expected response
        request_body=CategorySerializer(),  # Specify the request body serializer
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


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
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    lookup_field = "owner"


class CartView(APIView):
    """Endpoint: `/api/cart/`

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
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
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


    # @swagger_auto_schema(method='POST', request_body=CartSerializer)
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
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    """
        A get request to get all cart items and the code
        the code would be a comma(,) string containing the codes given to the customer by each store owner for a discounted price.

        As sooon as the code is typed in and the discount is applied and the user
        doesn't use it at the time it'll have been expired.
        """


    def get(self, request):
        """
        A get request to get all cart items and the code
        the code would be a comma(,) string containing the codes given to the customer by each store owner for a discounted price.

        As sooon as the code is typed in and the discount is applied and the user
        doesn't use it at the time it'll have been expired.
        """

        user = request.user
        data = request
        cart = Cart.objects.get(user=user, paid=False)
        code = request.query_params.get('code', None)

        # Calculate the total amount based on cart items
        products = CartItem.objects.filter(cart=cart, paid=False)
        # Calculate the total sum the user ought to pay and also try to find the discount if there's any for the user
        # TODO: CHECK IF THE CODE IS A LIST THEN FILTER BY IT
        # AND FILTER THE PRODUCTS AND GIVE THE DISCOUNT
        total_amount = sum(item.product.price * item.quantity for item in products)

        # Return the cart items and the total price to be paid by the user
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
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
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
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        store = request.user.my_store
        checkouts = Checkout.objects.filter(cart__items__category__store=store)
        serializer = CheckoutSerializer(checkouts, many=True)
        return Response(serializer.data, status=stat.HTTP_200_OK)

# GIVE DISCOUNT
@api_view(['POST'])
def give_discount(request):
    # Get the product based on the provided product ID
    """This endpoint is to e used by the seller to create a one time discoint for the buyer.

    Keyword arguments:
    product_id -- the id of the product that the buyer clicked on to initiate the chat with the seller
    user_id -- the id of the buyer
    percent -- the what is the percentage of the discount for the buyer (10, 20 , 20 ect)
    Return: {"code": "" } return a code that the buyer can make use of when making payment
    """

    data = request.data
    product_id = int(data['product_id'])
    user_id = int(data['user_id'])
    percent = float(data['percent'])/100

    # Find the product
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the current user is a vendor/seller
    if not request.user.is_authenticated or not request.user.is_seller:
        return Response({"message": "Unauthorized. Only vendors can give discounts."}, status=status.HTTP_401_UNAUTHORIZED)

    # Check if the discount has already been applied for the user and product
    user = User.objects.get(id=user_id)
    if Discount.objects.filter(user=user, product=product).exists():
        return Response({"message": "Discount already applied for this user and product."}, status=status.HTTP_400_BAD_REQUEST)

    # Apply the discount to the product
    discount = percent
    if not discount:
        return Response({"message": "Discount value is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # get the product and apply the percent discount
        product = Product.objects.get(id=product_id)
        amount = round(product.amount * percent, 2)
        code = utils.generate_discount_id()

        # Create a discount entry for the user and product
        Discount.objects.create(user=user, product=product, amount=amount, code=code)

        return Response({"message": "Discount applied successfully."}, status=status.HTTP_200_OK)
    except ValueError:
        return Response({"message": "Invalid discount value. Must be a number."}, status=status.HTTP_400_BAD_REQUEST)
