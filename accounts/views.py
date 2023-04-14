from django.core.mail import send_mail
from django.shortcuts import render
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model, login
from django.utils import timezone
from rest_framework import generics, mixins, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


from .models import SellerProfile, BuyerProfile
from .serializers import ChangePasswordSerializer, BuyerSerializer, SellerSerializer
from .utils import get_code
User = get_user_model()


# Create your views here.


class SellerCreateView(generics.CreateAPIView):
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
