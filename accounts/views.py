from datetime import datetime, timedelta

from django.contrib.auth import get_user_model, login
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, serializers, status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from payment.models import BankDetail
from payment.serializers import BankDetailSerializer
from store.models import Store
from store.serializers import AllStoreDetailSerializer, StoreSerializer

from .models import Address, MyUserAuth, Profile
from .serializers import (AddressSerializer, ProfileSerializer, BuyerSerializer, ChangePasswordSerializer, LoginSerializer, SellerSerializer)
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from drf_yasg import openapi
from .utils import get_code, send_verification_code

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Create your views here.
class LoginView(APIView):

    @csrf_exempt
    def post(self, request):
        data = request.data
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user, backend='accounts.authentication.EmailAuthBackend')
            auth_token = get_tokens_for_user(user=user)
            response_data = {
                "data": {
                    'id': user.id,
                    "last_name": user.last_name,
                    "first_name": user.first_name,
                    "username": user.username,
                    'email': user.email,
                    "jwt_token": auth_token
                },
                "errors": None,
                "status": "success",
                "message": "User created successfully",
                "pagination": {
                    "count": None,
                    "next": None,
                    "previous": None,
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        # return Response({"message": "Account not verified or wrong login info", })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FCMUpdateView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'fcm_token': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        operation_description="Update FCM token for user's profile",
        responses={
            200: "FCM token updated successfully",
            400: "Bad request",
            401: "Unauthorized",
        },
    )
    def post(self, request):
        user = request.user
        profile = Profile.objects.get(user=user)
        profile.fcm_token = request.data.get('fcm_token', None)
        profile.save()
        response_data = {
            "data": None,
            "errors": None,
            "status": "failed",
            "message": "FCM token updated",
            "pagination": {
                "count": None,
                "next": None,
                "previous": None,
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

class SellerCreateView(generics.CreateAPIView):
    # Disable CSRF protection for POST requests
    # http_method_names = ['post']

    serializer_class = SellerSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            # Validate the data
            serializer.is_valid(raise_exception=True)
            # Create the user
            user = serializer.save()

            # Prepare the response data
            # Adjust pagination count as needed
            response_data = {
                "data": serializer.data,
                "errors": None,
                "status": "success",
                "message": "User created successfully",
                "pagination": {
                    "count": None,
                    "next": None,
                    "previous": None,
                }
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Handle error response
            response_data = {
                "data": None,
                "errors": serializer.errors,
                "status": "failure",
                "message": "Something went wrong. Please try again.",
                "pagination": None
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class BuyerCreateView(generics.CreateAPIView):
    serializer_class = BuyerSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            # Validate the data
            serializer.is_valid(raise_exception=True)
            # Create the user
            user = serializer.save()

            # Prepare the response data
            # Adjust pagination count as needed
            response_data = {
                "data": serializer.data,
                "errors": None,
                "status": "success",
                "message": "User created successfully",
                "pagination": {
                    "count": None,
                    "next": None,
                    "previous": None,
                }
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Handle error response
            response_data = {
                "data": None,
                "errors": serializer.errors,
                "status": "failure",
                "message": "Something went wrong. Please try again.",
                "pagination": None
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        obj = self.request.user
        return obj

    def get_serializer_context(self):
        context = super(ChangePasswordView, self).get_serializer_context()
        context.update({
            'request': self.request
        })
        return context

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        request = self.request
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': True, 'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Filter addresses based on the authenticated user
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Check if the user has an existing address
        user_addresses = Address.objects.filter(user=self.request.user)
        if not user_addresses.exists():
            # If the user doesn't have an existing address, set is_default to True
            serializer.save(user=self.request.user, is_default=True)
        else:
            serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Addresses retrieved successfully",
            "pagination": None
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response_data = {
            "data": response.data,
            "errors": None,
            "status": "success",
            "message": "Address created successfully",
            "pagination": None
        }
        return Response(response_data, status=response.status_code)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Filter addresses based on the authenticated user
        return Address.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Address retrieved successfully",
            "pagination": None
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_data = {
            "data": serializer.data,
            "errors": None,
            "status": "success",
            "message": "Address updated successfully",
            "pagination": None
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        response_data = {
            "data": None,
            "errors": None,
            "status": "success",
            "message": "Address deleted successfully",
            "pagination": None
        }
        return Response(response_data, status=response.status_code)

class SellerProfileUpdateView(generics.UpdateAPIView):
    serializer_class = SellerSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

class BuyerProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

class BecomeBuyer(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.get(user=user)
        if profile.is_buyer:
            return Response({"message": "User is already a buyer"}, status=status.HTTP_200_OK)
        else:
            profile.is_buyer = True
            profile.save()
            return Response({"message": "User is now a buyer"}, status=status.HTTP_200_OK)

class BecomeSeller(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.get(user=user)
        if profile.is_seller:
            return Response({"message": "User is already a seller"}, status=status.HTTP_200_OK)
        else:
            profile.is_seller = True
            profile.save()
            # Create user store
            Store.objects.create(
                owner=user,
                title=f"{user.username}-store",
                slug=f"{user.username}-store-slug"
            )
            return Response({"message": "User is now a seller"}, status=status.HTTP_200_OK)

class ProfileView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Endpoint to get profile information",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                description="User ID",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'profile': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="Seller profile information",
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'sellerprofile': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'user': openapi.Schema(type=openapi.TYPE_STRING),
                                        'nin': openapi.Schema(type=openapi.TYPE_STRING),
                                        'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                                        'address': openapi.Schema(type=openapi.TYPE_STRING),
                                    },
                                ),
                            },
                        ),
                        'store': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="Store details",
                            properties={
                                'owner': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'chat_owner': openapi.Schema(type=openapi.TYPE_STRING),
                                'title': openapi.Schema(type=openapi.TYPE_STRING),
                                'slug': openapi.Schema(type=openapi.TYPE_STRING),
                                'categories': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                                            'slug': openapi.Schema(type=openapi.TYPE_STRING),
                                            'detail_edit_url': openapi.Schema(type=openapi.TYPE_STRING),
                                            'products': openapi.Schema(
                                                type=openapi.TYPE_ARRAY,
                                                items=openapi.Schema(
                                                    type=openapi.TYPE_OBJECT,
                                                    properties={
                                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                                                        'image': openapi.Schema(type=openapi.TYPE_STRING),
                                                        'description': openapi.Schema(type=openapi.TYPE_STRING),
                                                        'price': openapi.Schema(type=openapi.TYPE_STRING),
                                                        'slug': openapi.Schema(type=openapi.TYPE_STRING),
                                                        'detail_edit_url': openapi.Schema(type=openapi.TYPE_STRING),
                                                    },
                                                ),
                                            ),
                                        },
                                    ),
                                ),
                            },
                        ),

                                            },
                                        ),
                                    ),
                                    400: "Bad request. For example, when 'id' is missing or not a valid integer.",
                                    404: "User not found.",
                                }
                            )
    def get(self, request):
        user = request.user
        profile = Profile.objects.get(user=user)
        addresses = Address.objects.filter(user=user)
        banks = BankDetail.objects.filter(
            user=user) if BankDetail.objects.filter(user=user).exists() else None
        address_data = AddressSerializer(addresses, many=True).data
        # Check if the user is a seller
        profile_data = ProfileSerializer(instance=profile,).data
        profile_data["user_id"] = user.id
        profile_data["first_name"] = user.first_name
        profile_data["last_name"] = user.last_name
        profile_data["email"] = user.email
        print(banks)
        if profile.is_seller:
            store = StoreSerializer(instance=Store.objects.get(owner=user), context={"request": request}).data
            result = {
                'profile': profile_data,
                'store': store,
                "address":address_data,
                "bank_details": BankDetailSerializer(banks, many=True).data if banks else []
            }
            return Response(result, status=status.HTTP_200_OK)
        else:
            result = {
                'profile': profile_data,
                "address": address_data
            }
            return Response(result, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def reset_password_view(request):
    """
    Reset Password for a user.

    GET
    Send a verification code to the user's email address.

    - `email` (request data): The email address of the user.

    POST
    Reset the user's password using the verification code.

    - `email` (request data): The email address of the user.
    - `verification_code` (request data): The verification code received by the user.
    - `password` (request data): The new password for the user.

    Returns a JSON response with the following format:

    {
        "status": <bool>,
        "message": <str>
    }

    - `status`: Indicates the status of the operation (True for success, False for failure).
    - `message`: A message describing the result of the operation.

    GET Example Response (HTTP 200 OK):
    {
        "status": true,
        "message": "Verification code sent"
    }

    POST Example Response (HTTP 200 OK):
    {
        "status": true,
        "message": "Password reset successfully"
    }

    Error Responses:
    - HTTP 400 BAD REQUEST: If the required parameters are missing or invalid.
    - HTTP 404 NOT FOUND: If the user associated with the provided email address is not found.
    """

    if request.method == 'GET':
        print(request)
        # Send verification code to the user
        email = request.data.get('email')
        if not email:
            email = request.GET.get('email')
        if not email:
            return Response({'status': False, 'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'status': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        code = get_code()
        auth, created = MyUserAuth.objects.get_or_create(user=user)
        auth.code = code
        auth.save()
        # Implement your own email sending logic
        send_verification_code(email, code, "password")
        return Response({'status': True, 'message': 'Verification code sent'}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # Reset user password
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')
        password = request.data.get('password')

        if not email or not verification_code or not password:
            return Response({'status': False, 'message': 'Email, verification code, and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'status': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if MyUserAuth.expired.filter(user=user).exists():
            return Response({'status': False, 'message': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save()
        return Response({'status': True, 'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
