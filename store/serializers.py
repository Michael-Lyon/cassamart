from django.urls import reverse
from rest_framework import serializers

from accounts.serializers import AddressSerializer

from .models import Cart, CartItem, Category, Checkout, Product, Store, Ticket, WishlistItem, Image


class CategoryInlineSerializer(serializers.Serializer):
    owner = serializers.CharField(read_only=True )
    title = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    image = serializers.ImageField(read_only=True)
    detail_url = serializers.HyperlinkedIdentityField(
        view_name="store:category_detail",
        lookup_field='pk'
    )

class StoreInlineSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    owner = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    image = serializers.ImageField(read_only=True)
    detail_url = serializers.HyperlinkedIdentityField(
        view_name="store:store_detail",
        lookup_field='pk'
    )

class ProductsInlineSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True)
    description = serializers.CharField(read_only=True)
    price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    slug = serializers.SlugField(read_only=True)
    detail_edit_url = serializers.HyperlinkedIdentityField(
        view_name="store:product_detail_update",
        lookup_field='pk'
    )


class AllStoreDetailSerializer(serializers.ModelSerializer):
    chat_owner = serializers.SerializerMethodField()
    created = serializers.DateTimeField()
    class Meta:
        model = Store
        fields = ["id",'owner', "image" ,"chat_owner", "title", "created" ]


    def get_chat_owner(self, obj):
        owner = obj.owner
        request = self.context.get('request')
        if owner and request:
            receiver_id = owner.id
            chat_url = reverse('chat:chat_api', args=[receiver_id])
            return request.build_absolute_uri(chat_url)
        return None


class StoreSerializer(serializers.ModelSerializer):
    title = serializers.ReadOnlyField()
    slug = serializers.ReadOnlyField()
    class Meta:
        model = Store
        fields = ["id", 'title', "slug", "image",]

    def get_chat_owner(self, obj):
        owner = obj.owner
        request = self.context.get('request')
        if owner and request:
            receiver_id = owner.id
            chat_url = reverse('chat:chat_api', args=[receiver_id])
            return request.build_absolute_uri(chat_url)
        return None


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    chat_owner = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    store = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ["id", 'title', "images",  "description", "price", "stock", "available", "chat_owner", 'category', "store"]
        extra_kwargs = {
            'store': {'required': False, },
            # 'category': {'required': False},
            # 'store': {'required': False, },
        }

    def get_category(self, obj):
        my_category = obj.category
        return CategoryInlineSerializer(my_category, context=self.context).data

    def get_store(self, obj):
        my_store = obj.store
        return StoreInlineSerializer(my_store, context=self.context).data

    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.images.all()
        return [request.build_absolute_uri(img.image.url) for img in images]

    def get_chat_owner(self, obj):
        owner = obj.store.owner
        request = self.context.get('request')
        if owner and request:
            receiver_id = owner.id
            chat_url = reverse('chat:chat_api', args=[receiver_id])
            return request.build_absolute_uri(chat_url)
        return None



class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    class Meta:
        model = CartItem
        fields = '__all__'

    def to_representation(self, instance):
        # Use the original representation for read operations, including detailed product info
        representation = super().to_representation(instance)
        representation['product'] = ProductSerializer(
            instance.product, context={'request': self.context.get('request')}).data
        return representation

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['user',  'paid', 'items']


class CheckoutSerializer(serializers.ModelSerializer):
    cart = CartSerializer()
    delivery_address = AddressSerializer()
    class Meta:
        model = Checkout
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class WishlistItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    class Meta:
        model = WishlistItem
        fields = ("id", 'product', 'added_at')

    def validate_product(self, value):
        try:
            return Product.objects.get(pk=value.id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product ID.")

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        # Retrieve the product instance based on the provided ID
        product_id = validated_data['product']
        print(product_id)
        try:
            product = Product.objects.get(pk=product_id.id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product ID.")

        return WishlistItem.objects.create(user=user, product=product)

class WishlistItemGetSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = WishlistItem
        fields = ("id", 'added_at', 'product')

