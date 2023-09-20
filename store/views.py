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
from .my_permission  import IsSeller
from .models import (Cart, CartItem, Category, Checkout, Discount, Product, Store)
from .serializers import (AllStoreDetailSerializer, CartItemSerializer,
                          CartSerializer, CategorySerializer,
                          CheckoutSerializer, ProductSerializer,
                          StoreSerializer, TicketSerializer)
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()



class StoreListApiView(APIView):
    def get(self, request):
        # Paginate the queryset
        paginator = PageNumberPagination()
        paginator.page_size = 1  # You can adjust the page size as needed
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
    def get(self, request, store_id):
        try:
            paginator = PageNumberPagination()
            paginator.page_size = 1  # You can adjust the page size as needed
            store = Store.objects.get(id=store_id)
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



class CategoryList(APIView):
    def get(self, request):
        # Paginate the queryset
        paginator = PageNumberPagination()
        paginator.page_size = 1  # You can adjust the page size as needed
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
    def get(self, request, category_id):
        try:
            paginator = PageNumberPagination()
            paginator.page_size = 1  # You can adjust the page size as needed
            category = Category.objects.get(id=category_id)
            products = Product.objects.filter(category=category)
            result_page = paginator.paginate_queryset(products, request)
            serializer = ProductSerializer(result_page, many=True)
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
        paginator.page_size = 1  # You can adjust the page size as needed
        products = Product.objects.all()
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


class ProductCreateApiView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSeller()]  # Use the custom permission class
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser,)

    def create(self, request, *args, **kwargs):
        # Ensure that the user is the owner of the store associated with the product
        store_id = request.data.get('store')  # Assuming 'store' is the store field in the request data
        if store_id and request.user.store_set.filter(id=store_id).exists() and request.user.is_seller:
            # User is the owner of the store and is a seller, proceed with product creation
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            response_data = {
                "data": serializer.data,
                "errors": None,
                "status": "success",
                "message": "Product created successfully",
                "pagination": None
            }

            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"message": "You are not the owner of the store or you do not have seller privileges."}, status=status.HTTP_403_FORBIDDEN)








class ProductDetailUpdateApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSeller]  # Use the custom permission class

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Check successful",
            "pagination": None  # You can customize this if needed
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Format the response data as specified
            response_data = {
                "data": serializer.data,
                "errors": None,
                "status": "success",
                "message": "Check successful",
                "pagination": None  # You can customize this if needed
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
