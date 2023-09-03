from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.db import transaction
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.db.models import Q 
from store.models import Store

from .models import BuyerProfile, SellerProfile

User = get_user_model()


class SellerProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)

    class Meta:
        model = SellerProfile
        fields = ['user', 'nin', "phone_number", "address"]


class BuyerProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)

    class Meta:
        model = SellerProfile
        fields = ['user', "phone_number", "address"]


class SellerSerializer(serializers.ModelSerializer):
    sellerprofile = SellerProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'username', 'last_name', 'email',  'sellerprofile']

    def create(self, validated_data):
        try:
            # Check if a user with the same username or email already exists
            existing_user = User.objects.filter(Q(username=validated_data['username']) | Q(email=validated_data['email'])).first()
            if existing_user:
                raise serializers.ValidationError("A user with this username or email already exists.")

            profile_data = validated_data.pop('sellerprofile')
            print(profile_data)
            print(validated_data)
            user = User.objects.create_user(**validated_data)
            profile_data["user"] = user
            SellerProfile.objects.create(**profile_data)

            Store.objects.create(
                owner=user,
                title=f"{user.username}-store",
                slug=f"{user.username}-store-slug"
            )
            return user
        except Exception as e:
            print(e)
            user.delete()
            raise serializers.ValidationError("Something went wrong please try again")


class BuyerSerializer(serializers.ModelSerializer):
    buyerprofile = BuyerProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'username', 'last_name', 'password', 'email',  'buyerprofile']

    def create(self, validated_data):
        with transaction.atomic():
            profile_data = validated_data.pop('buyerprofile')
            try:
                # Check if a user with the same username or email already exists
                existing_user = User.objects.filter(Q(username=validated_data['username']) | Q(email=validated_data['email'])).first()
                if existing_user:
                    raise serializers.ValidationError("A user with this username or email already exists.")
                user = User.objects.create_user(**validated_data)
                profile_data["user"] = user
                BuyerProfile.objects.create(**profile_data)
                return user
            except Exception as e:
                print(e)
                user.delete()
                raise serializers.ValidationError("Something went wrong please try again")


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
        print(data)
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")
        # return data
