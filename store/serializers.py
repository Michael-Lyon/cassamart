from django.urls import reverse
from rest_framework import serializers

from .models import Cart, CartItem, Category, Checkout, Product, Store, Ticket, WishlistItem


class CategoryInlineSerializer(serializers.Serializer):
    owner = serializers.CharField(read_only=True )
    title = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    detail_edit_url = serializers.HyperlinkedIdentityField(
        view_name = "store:category_detail_update",
        lookup_field = 'pk'
    )
    products = serializers.SerializerMethodField(read_only=True)

    def get_products(self, obj):
        my_category = obj
        my_products = my_category.products.all()
        return ProductsInlineSerializer(my_products, many=True, context=self.context).data

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
        fields = ["id",'title', "slug", "image"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    store = serializers.CharField(read_only=True)
    class Meta:
        model = Product
        fields = ["id",'category', "store" ,'title', "image", "description", "price", "stock", "available", ]
        extra_kwargs = {
            'store': {'required': False, },
            # 'store': {'required': False, },
        }

    # def to_representation(self, instance):
    #     if isinstance(instance, Store):
    #         return {
    #             "id": instance.id,
    #             "store": instance.title,
    #             "title": instance.title,
    #             "image": instance.image,
    #             "description": instance.description,
    #             "price": instance.price,
    #             "stock": instance.stock,
    #             "available": instance.available
    #         }
    #     else:
    #         return super().to_representation(instance)



class CartItemSerializer(serializers.ModelSerializer):
    # product = ProductSerializer(source="product_set")
    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkout
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'




class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = ('user', 'product', 'added_at')
