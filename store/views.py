from datetime import timedelta, datetime
from decimal import Decimal
import json
import os
from django_filters.rest_framework import DjangoFilterBackend
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
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from accounts.models import Address, Profile
from casamart.notification_sender import send_push_notification
from casamart.utils import create_response
from payment.models import BankDetail
from python_paystack.managers import TransactionsManager
from python_paystack.objects.transactions import Transaction
from python_paystack.paystack_config import PaystackConfig
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.db import transaction

from store.store_filters import OrderFilter, ProductFilter, StoreFilter
from . import utils
from .my_permission import IsSellerIsOwner, isSeller
from .models import (CanceledCheckout, Cart, CartItem,
                     Category, Checkout, Discount, Product, Store, WishlistItem)
from .serializers import (AllStoreDetailSerializer, CartItemSerializer,
                          CartSerializer, CategorySerializer,
                          CheckoutSerializer, ImageSerializer, ProductSerializer,
                          StoreSerializer, TicketSerializer, WishlistItemGetSerializer, WishlistItemSerializer
                          )
from drf_yasg.utils import swagger_auto_schema
from dotenv import load_dotenv
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg import openapi

PAGINATION_NUM = 30

User = get_user_model()


class StoreListApiView(APIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = StoreFilter

    def get(self, request):
        """
        The function retrieves a paginated list of all stores, serializes the data, and returns it in a
        response along with pagination information.

        :param request: The `request` parameter in the `get` method is typically an object that contains
        information about the current HTTP request. It includes details such as the request method (GET,
        POST, etc.), headers, user authentication details, and query parameters. In this context, the
        `request` parameter is used
        :return: A paginated response containing data from the Store queryset, along with pagination
        information such as count, next page link, and previous page link. The response includes a
        success status, a message indicating a successful check, and no errors.
        """
        stores = Store.objects.all()
        filtered_data = self.filterset_class(request.GET, queryset=stores)

        # Paginate the queryset
        paginator = PageNumberPagination()
        paginator.page_size = PAGINATION_NUM  # You can adjust the page size as needed
        # Apply the filters
        result_page = paginator.paginate_queryset(filtered_data.qs, request)

        # Serialize the paginated queryset
        serializer = AllStoreDetailSerializer(
            result_page, many=True, context={"request": request})

        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Check successful",
            "pagination": {
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

# This class is an API view in Django REST framework that retrieves store details and associated
# products with pagination support.


class StoreDetailApiView(APIView):
    def get(self, request, pk):
        """
        This function retrieves store details and associated products with pagination support, handling
        cases where the store does not exist.
        
        :param request: The `request` parameter in the `get` method is typically an object that contains
        information about the current HTTP request. It includes details such as the request method (GET,
        POST, etc.), headers, user authentication details, and any data sent in the request body
        :param pk: The `pk` parameter in the `get` method represents the primary key of the Store object
        that you want to retrieve details for. It is used to uniquely identify a specific Store in the
        database
        :return: The code snippet provided is a Django view function that retrieves store details and
        associated products based on the store's primary key (pk). If the store with the given primary
        key exists, it returns a JSON response containing the store details, products, pagination
        information, and a success message with an HTTP status code of 200. If the store does not exist,
        it returns a JSON response indicating that the store
        """
        try:
            paginator = PageNumberPagination()
            paginator.page_size = PAGINATION_NUM  # You can adjust the page size as needed
            store = Store.objects.get(id=pk)
            store_data = AllStoreDetailSerializer(
                store, context={"request": request})
            products = Product.objects.filter(store=store)
            result_page = paginator.paginate_queryset(products, request)
            serializer = ProductSerializer(
                result_page, many=True, context={"request": request})
            response_data = {
                "data": {
                    'store_details': store_data.data,
                    'products': serializer.data
                },
                "errors": None,
                "status": "success",
                "message": "Check successful",
                "pagination": {
                    "count": paginator.page.paginator.count,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Store.DoesNotExist:
            response_data = {
                "data": None,
                "errors": None,
                "status": "failed",
                "message": "Store does not exist",
                "pagination": {
                    "count": None,
                    "next": None,
                    "previous": None,
                }
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class StoreDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    Endpoint: /api/store/<id>/
    Method: PUT
    Authentication: JWTAuthentication
    Permissions: IsAuthenticated, isSeller

    URL Parameters:
    - id: The ID of the store to be updated.

    Request Body:
    - JSON object containing the new details of the store.
    - 'image' field (optional) containing the image data as a file.

    Response:
    - 200 OK: If the update is successful. Returns a JSON object containing the updated store details.
    - 403 FORBIDDEN: If the user is not authorized to update the store. Returns a JSON object with "status": "error" and an error message.

    Note: Only the owner of the store can update the store details.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, isSeller)
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    lookup_field = "id"
    parser_classes = (MultiPartParser, JSONParser)

    def perform_update(self, serializer):
        # Ensure that only the store owner can update the store details
        user = self.request.user
        store = self.get_object()

        # Handle images separately
        if 'image' in self.request.FILES:
            for image_data in self.request.FILES.getlist('image'):
                if image_data:
                    store.image = image_data
                    store.save()

        if user == store.owner:
            serializer.save()
        else:
            response_data = {
                "status": "error",
                "message": "You are not authorized to update this store.",
            }
            return Response(response_data, status=status.HTTP_403_FORBIDDEN)


class SalesDataView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, store_id):
        paginator = PageNumberPagination()
        paginator.page_size = PAGINATION_NUM
        try:
            # Get the store and user from the request
            user = request.user
            store = Store.objects.get(id=store_id, owner=user)

            # Get the interval and category parameters from the query string
            interval = request.query_params.get('interval', None)
            category = request.query_params.get('category', None)

            # Determine the date range based on the interval
            today = datetime.now()
            if interval == 'weekly':
                start_date = today - timedelta(days=7)
            elif interval == 'monthly':
                start_date = today - timedelta(days=30)
            elif interval == 'yearly':
                start_date = today - timedelta(days=365)
            else:
                return Response({
                    "data": None,
                    "errors": {"message": "Invalid or missing interval parameter"},
                    "status": "error",
                    "message": "Check failed",
                    "pagination": None
                }, status=status.HTTP_400_BAD_REQUEST)

            # Filter checkouts based on category if provided
            checkout_data = Checkout.objects.filter(
                cart__items__store=store,
                updated__gte=start_date
            )

            # Sort checkouts by created date
            checkout_data = checkout_data.order_by('created')
            result_page = paginator.paginate_queryset(checkout_data, request)

            # Create a dictionary for the bar chart data
            chart_data = {}
            for checkout in result_page:
                date_key = checkout.created.strftime('%Y-%m-%d')
                chart_data[date_key] = chart_data.get(
                    date_key, 0) + checkout.total_amount

            return Response({
                "data": {"sales_data": chart_data},
                "errors": None,
                "status": "success",
                "message": "Check successful",
                "pagination": {
                    "count": paginator.page.paginator.count,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                }
            }, status=status.HTTP_200_OK)

        except Store.DoesNotExist:
            return Response({
                "data": chart_data,
                "errors": {"message": "Store not found"},
                "status": "error",
                "message": "Check failed",
                "pagination": None
            }, status=status.HTTP_404_NOT_FOUND)


class CategoryList(APIView):
    def get(self, request):
        # Paginate the queryset
        paginator = PageNumberPagination()
        paginator.page_size = PAGINATION_NUM  # You can adjust the page size as needed
        categories = Category.objects.all()
        result_page = paginator.paginate_queryset(categories, request)

        # Serialize the paginated queryset
        serializer = CategorySerializer(
            result_page, many=True, context={"request": request})

        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Check successful",
            "pagination": {
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CategoryDetail(APIView):
    def get(self, request, pk):
        try:
            paginator = PageNumberPagination()
            paginator.page_size = 30  # You can adjust the page size as needed
            category = Category.objects.get(id=pk)
            products = Product.objects.filter(
                category=category).order_by("-created")
            result_page = paginator.paginate_queryset(products, request)
            serializer = ProductSerializer(
                result_page, many=True, context={"request": request})
            response_data = {
                "data": serializer.data,
                "errors": None,
                "status": "success",
                "message": "Check successful",
                "pagination": {
                    "count": paginator.page.paginator.count,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            response_data = {
                "data": None,
                "errors": None,
                "status": "failed",
                "message": "Category does not exist",
                "pagination": {
                    "count": None,
                    "next": None,
                    "previous": None,
                }
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class ProductListApiView(APIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get(self, request):
        # Get all products
        products = Product.objects.all().order_by("-created")

        # Apply the filters
        filtered_data = self.filterset_class(request.GET, queryset=products)

        # Paginate the filtered queryset
        paginator = PageNumberPagination()
        paginator.page_size = PAGINATION_NUM  # You can adjust the page size as needed
        result_page = paginator.paginate_queryset(filtered_data.qs, request)

        # Serialize the paginated queryset
        serializer = ProductSerializer(
            result_page, many=True, context={"request": request})

        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Check successful",
            "pagination": {
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ProductDetailApiView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Product details retrieved successfully",
            "pagination": None
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ProductCreateApiView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [isSeller]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser,)

    def perform_create(self, serializer):
        store = Store.objects.get(owner=self.request.user)

        if not store:
            # Handle the case where the user does not own a store
            return Response(
                {
                    "data": None,
                    "errors": "User does not own a store",
                    "status": "error",
                    "message": "You need to be the owner of a store to create a product",
                    "pagination": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Create a list to store Image instances
        images_list = []

        # Handle images separately
        for image_data in self.request.FILES.getlist('images', []):
            image_serializer = ImageSerializer(data={'image': image_data})
            if image_serializer.is_valid():
                image_serializer.save()
                images_list.append(image_serializer.instance)
            else:
                # Handle the case where an image is not valid
                return Response(
                    {
                        "data": None,
                        "errors": image_serializer.errors,
                        "status": "error",
                        "message": "Image validation failed",
                        "pagination": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        category = Category.objects.get(id=self.request.data.get('category'))
        # Assign the store and images to the product before saving
        serializer.validated_data['store'] = store
        serializer.validated_data['images'] = images_list
        serializer.validated_data['category'] = category

        super().perform_create(serializer)

        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Product created successfully",
            "pagination": None,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class ProductDeleteApiView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSellerIsOwner]
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not user_has_permission_to_delete_product(request.user, instance):
            return Response(
                {
                    "data": None,
                    "errors": "Permission denied",
                    "status": "error",
                    "message": "You do not have permission to delete this product",
                    "pagination": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        self.perform_destroy(instance)
        return Response(
            {
                "data": None,
                "errors": None,
                "status": "success",
                "message": "Product deleted successfully",
                "pagination": None,
            },
            status=status.HTTP_204_NO_CONTENT,
        )


def user_has_permission_to_delete_product(user, product):
    # Add your custom logic to check if the user has permission to delete the product
    # For example, you might want to check if the user is the owner of the store associated with the product.
    store_owner = product.store.owner
    return user == store_owner


class ProductDetailUpdateApiView(generics.RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [isSeller]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (JSONParser, MultiPartParser,)
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Product details retrieved successfully",
            "pagination": None,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Ensure that the user is the owner of the store associated with the product
        if request.user != instance.store.owner:
            return Response(
                {
                    "data": None,
                    "errors": "User is not the owner of the store",
                    "status": "error",
                    "message": "You can only update products for your own store",
                    "pagination": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Product updated successfully",
            "pagination": None,
        }

        return Response(response_data, status=status.HTTP_200_OK)

# TODO: CHECK AND MAKE SURE THE CARD IS ONL


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

    def get_cart_total(self, cart):
        total_cost = Decimal(0)

        for cart_item in CartItem.objects.filter(cart=cart):
            total_cost += cart_item.product.price * cart_item.quantity

        return total_cost

    def get(self, request):
        user = request.user
        try:
            cart = Cart.objects.filter(user=user, paid=False).first()
            if cart:
                serializer = CartSerializer(
                    cart,  context={'request': request})
                data = serializer.data
                data["total_cost"] = self.get_cart_total(cart)
                response_data = {
                    "data": data,
                    "errors": None,
                    "status": "success",
                    "message": "User's cart retrieved successfully",
                    "pagination": None
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "data": None,
                    "errors": None,
                    "status": "success",
                    "message": "Cart is empty",
                    "pagination": None
                }
                return Response(response_data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            response_data = {
                "data": None,
                "errors": "Cart not found",
                "status": "error",
                "message": "Cart does not exist for the user",
                "pagination": None
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        data = request.data
        print(data)

        try:
            cart = Cart.objects.get(user=user, paid=False)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=user)

        data["cart"] = cart.id
        serializer = CartItemSerializer(
            data=data, context={'request': request})
        if serializer.is_valid():
            print(serializer.validated_data)
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']

            try:
                cart_item = CartItem.objects.get(cart=cart, product=product)
                cart_item.quantity += quantity
                cart_item.save()
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(
                    cart=cart, product=product, quantity=quantity)

            # Refresh the cart instance to include updated items
            cart.refresh_from_db()

            # Serialize the entire Cart object
            cart_serializer = CartSerializer(
                cart, context={'request': request})

            response_data = {
                "data": cart_serializer.data,  # Serialize the entire Cart object
                "errors": None,
                "status": "success",
                "message": "Item added to cart",
                "pagination": None
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        response_data = {
            "data": None,
            "errors": "Invalid data",
            "status": "error",
            "message": serializer.errors,
            # "message": "Product not found",
            "pagination": None
        }

        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user
        data = request.data
        cart = Cart.objects.get(user=user, paid=False)
        product_id = data.get('product')
        quantity = data.get('quantity')
        try:
            cart_item = CartItem.objects.get(cart=cart, product__id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
        except Cart.DoesNotExist:
            return Response(status=stat.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_200_OK)

    def delete(self, request):
        user = request.user
        data = request.data

        try:
            cart = Cart.objects.get(user=user, paid=False)
            cart_item = CartItem.objects.get(
                cart=cart, product__id=data['product'])
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
        data = None
        cart = Cart.objects.filter(user=user, paid=False).first()
        if cart:
            # Calculate the total amount based on cart items
            products = CartItem.objects.filter(cart=cart)
            # Calculate the total sum the user ought to pay and also try to find the discount if there's any for the user
            # TODO: CHECK IF THE CODE IS A LIST THEN FILTER BY IT
            # AND FILTER THE PRODUCTS AND GIVE THE DISCOUNT
            total_amount = sum(item.product.price *
                               item.quantity for item in products)

            # Return the cart items and the total price to be paid by the user
            serializer = CartSerializer(cart, context={'request': request})
            data = serializer.data
            data["total_amount"] = total_amount

            # INITAILIZE Paystack Transaction
            transaction = Transaction(
                email=user.email, amount=int(total_amount * 100))

            transaction_data = TransactionsManager().initialize_transaction(
                method="STANDARD", transaction=transaction)

            response = json.loads(transaction_data.to_json())
            data["paystack_details"] = response
            response_data = {
                "data": data,
                "errors": None,
                "status": "success",
                "message": "Cart items and total amount retrieved successfully",
                "pagination": None
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "data": data,
                "errors": None,
                "status": "success",
                "message": "Cart is empty",
                "pagination": None
            }
            return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            user = request.user
            cart = Cart.objects.filter(user=user, paid=False).first()

            if not cart:
                raise ValueError("No active cart found for the user.")

            data = request.data
            address_id = int(data.get("delivery_address", 0))
            total_amount = data.get("total_amount")
            reference = data.get("reference")

            if not address_id or not total_amount or not reference:
                raise ValueError(
                    "Missing required data: 'delivery_address', 'total_amount', or 'reference'.")

            try:
                delivery_address = Address.objects.get(id=address_id)
            except ObjectDoesNotExist:
                raise ValueError("Invalid delivery address ID.")

            # Wrap the process in a transaction to ensure atomicity
            with transaction.atomic():
                # Check payment status
                _status = utils.check_payment(reference)
                if _status != 'success':
                    return Response({
                        "data": None,
                        "errors": None,
                        "status": "failure",
                        "message": "Payment failed or not successful",
                        "pagination": None
                    }, status=status.HTTP_400_BAD_REQUEST)

                # If payment is successful, create or get checkout and mark the cart as paid
                checkout, created = Checkout.objects.get_or_create(
                    user=user, cart=cart, total_amount=total_amount,
                    status='paid', delivery_address=delivery_address,
                    payment_status=True
                )

                # Mark the cart as paid only after successful processing
                cart.paid = True
                cart.save()

                # Send email notifications to store owners about the order
                utils.send_order_mail(cart)

                # Send email notifications to buyer about purchase
                utils.send_buyer_order_mail(cart, user)

                # Get FCM tokens of the store owners
                fcm_tokens = checkout.get_unique_store_owners()

                # Send push notifications to store owners
                for fcm_token in fcm_tokens:
                    if fcm_token.strip():
                        message = "A user has placed a confirmed order containing products from your store."
                        send_push_notification(
                            fcm_token, title="Confirmed Order", body=message)

                # Send push notification to the user
                user_fcm_token = Profile.objects.get(user=user).fcm_token
                send_push_notification(user_fcm_token, title="Confirmed Order",
                                       body="Your order has been confirmed and will be delivered shortly.")

                # Successful transaction response
                return Response({
                    "data": None,
                    "errors": None,
                    "status": "success",
                    "message": "Transaction successful",
                    "pagination": None
                }, status=status.HTTP_202_ACCEPTED)

        except ObjectDoesNotExist as e:
            # Handle case where related objects (like Cart, Address) don't exist
            return Response({
                "data": None,
                "errors": str(e),
                "status": "error",
                "message": "Object not found. Please check your inputs.",
                "pagination": None
            }, status=status.HTTP_404_NOT_FOUND)

        except ValueError as e:
            # Handle missing or invalid data errors
            return Response({
                "data": None,
                "errors": str(e),
                "status": "error",
                "message": "Invalid input data. " + str(e),
                "pagination": None
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                "data": None,
                "errors": str(e),
                "status": "error",
                "message": "An unexpected error occurred. Please try again.",
                "pagination": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelCheckout(APIView):
    """
    ### This view is used to cancel an order
    **GET request**
    - no parameters are expected. This is merely too check that a user has bankdetails saved or not. your response would be
    ```json
        {
            "data": null,
            "errors": null,
            "status": "success",
            "pagination": null,
            message": "exists" / "not-exists"
        }
    ```
    **POST request**
    - data to be sent to backend are:
    - id of the checkout
    - bank_id: id of the bank they'll like to receive
    - reason: reason for cancellation
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        detail = BankDetail.objects.filter(user=user).exists()
        if detail:
            return Response(create_response(message="exists", status="success"))
        return Response(create_response(message="not-exists", status="success"))

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        checkout_id = data.get('checkout_id', None)
        bank_id = data.get('bank_id', None)
        reason = data.get('reason', None)

        if not checkout_id or not bank_id or not reason:
            return Response(create_response(message="All fields are required",))

        checkout: Checkout = Checkout.objects.filter(id=checkout_id).first(
        ) if Checkout.objects.filter(id=checkout_id).exists() else None

        bank_detail = BankDetail.objects.get(
            id=bank_id) if BankDetail.objects.filter(id=bank_id).exists() else None

        if not (checkout and bank_detail):
            return Response(create_response(message="Checkout or Bank Id is invalid ",))

        try:
            # Check if a CanceledCheckout already exists for this Checkout
            existing_canceled_checkout = CanceledCheckout.objects.get(
                checkout=checkout)
            return Response(create_response(message="This checkout has already been canceled."))

        except CanceledCheckout.DoesNotExist:
            # If it doesn't exist, create a new CanceledCheckout instance
            canceled_checkout = CanceledCheckout.objects.create(
                checkout=checkout,
                cancel_reason=reason,
                refund_bank_details=bank_detail
            )
            checkout.status = 'cancelled'
            checkout.save()
        # TODO: MAKE PUSH NOTIFICATIONS A BACKGROUND TASK
        fcm_tokens = canceled_checkout.get_unique_store_owners()

        # Send push notifications to the store owners
        for fcm_token in fcm_tokens:
            if fcm_token.strip() != "":
                message = f"A user has canceled a checkout containing products from your store."
                send_push_notification(
                    fcm_token, title="Cancelled Order", body=message)
        send_push_notification(Profile.objects.get(user=user).fcm_token, title="Cancelled Order",
                               body="Your order has been canceled and currently under review. We'll get in touch with you in a bit.")
        return Response(create_response(message="Order Cancelled", status="success",))


# The `MyOrders` class retrieves orders associated with the authenticated user's store using Django
# filters and returns the data in a serialized format.
class MyOrders(APIView):
    """
    ## My Orders

    This endpoint retrieves the orders for a seller. It can be filtered using the following parameters:

    #### Filters

    - **status**: Filter by order status. Possible values: `pending`, `not-paid`, `paid`.
    - **received_status**: Filter by received status. Possible values: `true`, `false`.

    - **products**: Filter by products. Possible values: product name
    #### Example

    To get all paid orders created between January 1, 2024, and December 31, 2024, the URL would be: ~created_after=2024-01-01&created_before=2024-12-31~

    `GET /api/orders?status=paid&&received_status=true&product=apple`
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get(self, request):
        store = request.user.my_store.get()
        checkouts = checkouts = Checkout.objects.filter(
            cart__items__store=store).distinct()
        filtered_data = OrderFilter(request.GET, queryset=checkouts)
        print(f"HEYYYYYY: {filtered_data.qs}")
        serializer = CheckoutSerializer(
            filtered_data.qs, many=True, context={'request': request})
        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "User's orders retrieved successfully",
            "pagination": None
        }
        return Response(response_data, status=status.HTTP_200_OK)


class MyStore(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        store = request.user.my_store.get()

        # Filter for check out and find total revenue and total cost of products
        checkouts = Checkout.objects.filter(
            cart__items__store=store).distinct()
        orders = CheckoutSerializer(
            checkouts, many=True, context={'request': request})
        # paid_checkouts = checkouts.filter(payment_status=True)

        # total_paid_amount = paid_checkouts.aggregate(
        #     total_amount=Sum('total_amount'))['total_amount']

        response_data = {
            "data": {
                "recent_orders": orders.data,
                # "total_revenue": total_paid_amount,
                "total_orders": checkouts.count(),
                "my_products": store.total_products()
            },
            "errors": None,
            "status": "success",
            "message": "User's orders retrieved successfully",
            "pagination": None
        }
        return Response(response_data, status=status.HTTP_200_OK)


class GoodsDelivered(APIView):
    """ ###GOODS DELIVERED ENDPOINT
    **POST**:
    Indicate a goods has been received.

    This endpoint through post gets a product id which indicates that the user has received the product and then makes payment to the owner of the product

    **PayLoad:**
    - product_id: The product id to resolve.
    - checkout_id: The checkout id to resolve.

    ### EXPECTED RESPONSE
    ```json
    {
        "data": null,
        "errors": null,
        "status": "success",
        "message": "Updated Successfully",
        "pagination": {
            "count": null,
            "next": null,
            "previous": null
        }
    }
    ```
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        user = request.user

        product_id = data.get('product_id')
        checkout_id = data.get('checkout_id')

        if not product_id or not checkout_id:
            return Response(create_response(message="Product ID and Checkout ID are required"), status=status.HTTP_400_BAD_REQUEST)

        try:
            checkout = get_object_or_404(Checkout, pk=checkout_id)
            cart_item = get_object_or_404(
                CartItem, product__id=product_id, cart=checkout.cart)

            # Mark the item as delivered
            cart_item.delivered = True
            cart_item.save()

            # Send push notification to buyer
            fcm_token = Profile.objects.get(user=checkout.user).fcm_token
            if fcm_token:
                send_push_notification(
                    token=fcm_token,
                    title="Order Delivered",
                    body="Order has been delivered, please verify recipient"
                )

            # Check if all items in the checkout are delivered and update checkout status
            checkout.check_received_status()

            return Response(create_response(message="Updated Successfully", status="success"))

        except (CartItem.DoesNotExist, Checkout.DoesNotExist):
            return Response(create_response(message="Cart or Product not found"), status=status.HTTP_404_NOT_FOUND)

class BuyerOrders(APIView):
    """
    ## My Orders

    This endpoint retrieves the orders for a seller. It can be filtered using the following parameters:

    #### Filters

    - **status**: Filter by order status. Possible values: `pending`, `not-paid`, `paid`.
    - **received_status**: Filter by received status. Possible values: `true`, `false`.

    - **products**: Filter by products. Possible values: product name
    #### Example

    To get all paid orders created between January 1, 2024, and December 31, 2024, the URL would be: ~created_after=2024-01-01&created_before=2024-12-31~

    `GET /api/orders?status=paid&&received_status=true&product=apple`
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get(self, request):
        checkouts = Checkout.objects.filter(user=request.user)
        filtered_data = OrderFilter(request.GET, queryset=checkouts)
        serializer = CheckoutSerializer(
            filtered_data.qs, many=True, context={'request': request})
        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "User's orders retrieved successfully",
            "pagination": None
        }
        return Response(response_data, status=status.HTTP_200_OK)


class WishlistItemCreateView(generics.CreateAPIView):
    queryset = WishlistItem.objects.all()
    authentication_classes = (JWTAuthentication,)
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Assuming your serializer has a 'product' field
        product_id = request.data.get('product')

        # Check if the product already exists in the Wishlist for the authenticated user
        existing_wishlist_item = WishlistItem.objects.filter(
            user=request.user, product=product_id).first()

        if existing_wishlist_item:
            # Product already exists, you can choose to return an error or update the existing item
            response_data = {
                "data": None,
                "errors": {"product": ["Product already exists in the Wishlist."]},
                "status": "error",
                "message": "Product already exists in the Wishlist.",
                "pagination": None
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Wishlist item created successfully",
            "pagination": None
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class WishlistItemListView(generics.ListAPIView):
    serializer_class = WishlistItemGetSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Wishlist items retrieved successfully",
            "pagination": None
        }

        return Response(response_data, status=status.HTTP_200_OK)


class WishlistItemDeleteView(generics.DestroyAPIView):
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (JWTAuthentication,)
    lookup_field = "pk"

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        response_data = {
            "data": None,
            "errors": None,
            "status": "success",
            "message": "Wishlist item deleted successfully",
            "pagination": None
        }

        return Response(response_data, status=status.HTTP_204_NO_CONTENT)


class GiveDiscountAPIView(APIView):
    """
    This endpoint is used by the seller to create a one-time discount for the buyer.

    Keyword arguments:
    product_id -- the id of the product that the buyer clicked on to initiate the chat with the seller
    user_id -- the id of the buyer
    percent -- the percentage of the discount for the buyer (10, 20, 30, etc.)

    Return: {"code": ""} return a code that the buyer can make use of when making payment
    """

    def post(self, request):
        data = request.data
        product_id = int(data['product_id'])
        user_id = int(data['user_id'])
        percent = float(data['percent']) / 100

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_authenticated or not request.user.is_seller:
            return Response({"message": "Unauthorized. Only vendors can give discounts."}, status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.get(id=user_id)

        if Discount.objects.filter(user=user, product=product).exists():
            return Response({"message": "Discount already applied for this user and product."}, status=status.HTTP_400_BAD_REQUEST)

        discount = percent
        if not discount:
            return Response({"message": "Discount value is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = round(product.amount * percent, 2)
            code = utils.generate_discount_id()
            Discount.objects.create(
                user=user, product=product, amount=amount, code=code)

            return Response({"code": code, "message": "Discount applied successfully."}, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"message": "Invalid discount value. Must be a number."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def give_discount(request):
    give_discount_view = GiveDiscountAPIView.as_view()
    return give_discount_view(request)


class SendMessageNotificationView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Send a notification message",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'receiver_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['message', 'receiver_id']
        ),
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': openapi.Schema(type=openapi.TYPE_STRING),
                'errors': openapi.Schema(type=openapi.TYPE_STRING),
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'pagination': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )}
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        message = data.get("message")
        receiver_id = data.get("receiver_id")
        response_data = {}

        if not message or not receiver_id:
            response_data['errors'] = 'Message or receiver_id is missing'
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = Profile.objects.get(user__id=receiver_id)
            send_push_notification(profile.fcm_token, "New Message", message)
            response_data.update({
                "status": "success",
                "message": "Message sent successfully"
            })
            return Response(data=response_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            response_data['errors'] = 'Profile not found for the given receiver_id'
            return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data['errors'] = str(e)
            return Response(data=response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
