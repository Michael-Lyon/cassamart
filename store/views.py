from datetime import timedelta, datetime
from decimal import Decimal
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
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from accounts.models import Wallet
from python_paystack.managers import TransactionsManager

from . import utils
from .my_permission  import IsSellerIsOwner, isSeller
from .models import (Cart, CartItem, Category, Checkout, Discount, Product, Store, WishlistItem)
from .serializers import (AllStoreDetailSerializer, CartItemSerializer,
                            CartSerializer, CategorySerializer,
                            CheckoutSerializer, ImageSerializer, ProductSerializer,
                            StoreSerializer, TicketSerializer, WishlistItemGetSerializer, WishlistItemSerializer
                        )
from drf_yasg.utils import swagger_auto_schema
PAGINATION_NUM = 30

User = get_user_model()



class StoreListApiView(APIView):
    def get(self, request):
        # Paginate the queryset
        paginator = PageNumberPagination()
        paginator.page_size = PAGINATION_NUM  # You can adjust the page size as needed
        stores = Store.objects.all()
        result_page = paginator.paginate_queryset(stores, request)

        # Serialize the paginated queryset
        serializer = AllStoreDetailSerializer(result_page, many=True, context={"request": request})

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

class StoreDetailApiView(APIView):
    def get(self, request, pk):
        try:
            paginator = PageNumberPagination()
            paginator.page_size = PAGINATION_NUM  # You can adjust the page size as needed
            store = Store.objects.get(id=pk)
            store_data = AllStoreDetailSerializer(store, context={"request": request})
            products = Product.objects.filter(store=store)
            result_page = paginator.paginate_queryset(products, request)
            serializer = ProductSerializer(result_page, many=True, context={"request": request})
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
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, isSeller)
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    lookup_field = "id"

    def perform_update(self, serializer):
        # Ensure that only the store owner can update the store details
        user = self.request.user
        store = self.get_object()

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
        serializer = CategorySerializer(result_page, many=True, context={"request":request})

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
            products = Product.objects.filter(category=category).order_by("-created")
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
    def get(self, request):
        # Paginate the queryset
        paginator = PageNumberPagination()
        paginator.page_size = PAGINATION_NUM  # You can adjust the page size as needed
        products = Product.objects.all().order_by("-created")
        result_page = paginator.paginate_queryset(products, request)

        # Serialize the paginated queryset
        serializer = ProductSerializer(result_page, many=True, context={"request": request})

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

    def create(self, request, *args, **kwargs):
        store = Store.objects.get(owner=request.user)
        print(store)
        print(store.id)
        if not store:
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
        for image_data in request.FILES.getlist('images', []):
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


        # Modify the request data to include the store and images

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Assign the store to the product before saving
        serializer.validated_data['store'] = store
        serializer.validated_data['images'] = images_list

        self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)

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
    parser_classes = (MultiPartParser,)
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
            cart = Cart.objects.get(user=user)
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
            "message": "Invalid data for cart item",
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
            cart_item = CartItem.objects.get(cart=cart, product__id=data['product'])
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
        products = CartItem.objects.filter(cart=cart)
        # Calculate the total sum the user ought to pay and also try to find the discount if there's any for the user
        # TODO: CHECK IF THE CODE IS A LIST THEN FILTER BY IT
        # AND FILTER THE PRODUCTS AND GIVE THE DISCOUNT
        total_amount = sum(item.product.price * item.quantity for item in products)

        # Return the cart items and the total price to be paid by the user
        serializer = CartSerializer(cart, context={'request': request})
        data = serializer.data
        data["total_amount"] = total_amount
        response_data = {
            "data": data,
            "errors": None,
            "status": "success",
            "message": "Cart items and total amount retrieved successfully",
            "pagination": None
        }
        return Response(response_data, status=status.HTTP_200_OK)

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
            response_data = {
                "data": serializer.data,
                "errors": None,
                "status": "success",
                "message": "Transaction successful",
                "pagination": None
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        else:
            response_data = {
                "data": None,
                "errors": None,
                "status": "error",
                "message": "Failed Transaction try again",
                "pagination": None
            }
            return Response(response_data, status=stat.HTTP_402_PAYMENT_REQUIRED)

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
            response_data = {
                "data": {"message": "Updated."},
                "errors": None,
                "status": "success",
                "message": "Goods received updated successfully",
                "pagination": None
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({"message":"Updated."} , status=stat.HTTP_409_CONFLICT)

class MyOrders(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        store = request.user.my_store
        checkouts = Checkout.objects.filter(cart__items__store=store)
        serializer = CheckoutSerializer(checkouts, many=True)
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