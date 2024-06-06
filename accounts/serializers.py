from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from django.db.models import Q
import traceback

from store.models import Store

from .models import Address, Profile
from payment.models import BankDetail
from payment.serializers import BankDetailInlineSerializer, BankDetailSerializer

User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address', 'latitude', 'longitude', "is_default"]

class ProfileSerializer(serializers.ModelSerializer):
    user_detail = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ['phone_number', 'address',
                    "is_buyer", "is_seller", "user_detail"]

    def get_user_detail(self, obj):
        if  isinstance(obj, User):
            return {
                "id": obj.id,
                "email": obj.email,
                "first_name": obj.first_name,
                "last_name": obj.last_name
            }
        return {
            "id": obj.user.id,
            "email": obj.user.email,
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name
        }

class SellerSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'username', 'last_name', 'email', 'password', 'profile']

    def create(self, validated_data):
        user = None
        with transaction.atomic():
            try:
                # Check if a user with the same username or email already exists
                existing_user = User.objects.filter(Q(username=validated_data['username']) | Q(email=validated_data['email'])).first()
                if existing_user:
                    raise serializers.ValidationError("A user with this username or email already exists.")

                #  POP THE P[ROFILE DATA]
                profile_data = validated_data.pop('profile')

                # CREATE USER
                user = User.objects.create_user(**validated_data)
                profile_data["user"] = user
                profile_data["is_seller"] = True
                Profile.objects.create(**profile_data)

                #create user store
                Store.objects.create(
                    owner=user,
                    title=f"{user.username}-store",
                    slug=f"{user.username}-store-slug"
                )
                user.save()
                return user

            except Exception as e:
                print(e)
                traceback.print_exc()
                if user:
                    user.delete()
                raise serializers.ValidationError("A user has already been created with this username and or email address.")

class BuyerSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'username', 'last_name', "password", 'email', 'profile']

    def create(self, validated_data):
        with transaction.atomic():
            try:
                # Check if a user with the same username or email already exists
                existing_user = User.objects.filter(Q(username=validated_data['username']) | Q(email=validated_data['email'])).first()
                if existing_user:
                    raise serializers.ValidationError("A user with this username or email already exists.")

                profile_data = validated_data.pop('profile')
                user = User.objects.create_user(**validated_data)
                profile_data["user"] = user
                profile_data["is_buyer"] = True
                Profile.objects.create(**profile_data)

                return user
            except Exception as e:
                print(e)
                traceback.print_exc()
                user.delete()
                raise serializers.ValidationError("Something went wrong, please try again")

class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.context.get('request', None)
        return context

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.instance
        if not user.check_password(value):
            raise serializers.ValidationError({"message": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        print(user)
        if user and user.is_active:
            return user
        raise serializers.ValidationError(detail={
                'username': 'Check your username.',
                'password': 'Check your password.'
            }, code="authentication_failed")


