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

from store.models import Store
from store.serializers import AllStoreDetailSerializer, StoreSerializer

from .models import Profile
from .serializers import (ProfileSerializer, BuyerSerializer, ChangePasswordSerializer, LoginSerializer, SellerSerializer)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import get_code

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
            return Response({"message": "User Logged in", "data": {
                'id': user.id,
                "last_name": user.last_name,
                "first_name": user.first_name,
                "username": user.username,
                'email': user.email,
                "jwt_token": auth_token
            }})
        # return Response({"message": "Account not verified or wrong login info", })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellerCreateView(generics.CreateAPIView):
    # Disable CSRF protection for POST requests
    # http_method_names = ['post']

    serializer_class = SellerSerializer
    queryset = User.objects.all()


class BuyerCreateView(generics.CreateAPIView):
    serializer_class = BuyerSerializer
    queryset = User.objects.all()


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
        # Check if the user is a seller
        profile_data = ProfileSerializer(instance=profile,).data
        profile_data["first_name"] = user.first_name
        profile_data["last_name"] = user.last_name
        profile_data["email"] = user.email
        if profile.is_seller:
            store = StoreSerializer(instance=Store.objects.get(owner=user), context={"request": request}).data
            result = {
                'profile': profile_data,
                'store': store,
            }
            return Response(result, status=status.HTTP_200_OK)
        else:
            result = {
                'profile': profile_data,
            }
            return Response(result, status=status.HTTP_200_OK)




