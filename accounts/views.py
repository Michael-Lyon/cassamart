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
from store.serializers import AllStoreDetailSerializer

from .models import BuyerProfile, SellerProfile
from .serializers import (BuyerProfileSerializer, BuyerSerializer, ChangePasswordSerializer, LoginSerializer, SellerProfileSerializer, SellerSerializer)
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
            login(request, user)
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
    http_method_names = ['post']

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
    serializer_class = SellerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return SellerProfile.objects.get(user=self.request.user)


class BuyerProfileUpdateView(generics.UpdateAPIView):
    serializer_class = BuyerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return BuyerProfile.objects.get(user=self.request.user)


class ProfileView(APIView):
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
        id = request.query_params.get('id')

        # Validate inputs
        if not id:
            return Response({"message": "Both 'id' must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            id = int(id)
        except ValueError:
            return Response({"message": "'id' must be a valid integer"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user or return 404 if not found
        user = get_object_or_404(User, id=id)

        # Check if the user is a seller
        if hasattr(user, 'sellerprofile'):
            profile = SellerSerializer(instance=user).data
            store = AllStoreDetailSerializer(instance=Store.objects.get(owner=user)).data
            result = {
                'profile': profile,
                'store': store,
            }
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User is not a seller"}, status=status.HTTP_400_BAD_REQUEST)




