from django.urls import reverse
from rest_framework import serializers

from .models import Cart, CartItem, Category, Checkout, Product, Store, Ticket


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
    categories = serializers.SerializerMethodField(read_only=True)
    chat_owner = serializers.SerializerMethodField()
    class Meta:
        model = Store
        fields = ['owner',  "chat_owner", "title", "slug","categories" ]


    def get_categories(self, obj):
        store = obj
        my_categories = store.categories.all()
        return CategoryInlineSerializer(my_categories, many=True, context=self.context).data


    def get_chat_owner(self, obj):
        owner = obj.owner
        request = self.context.get('request')
        if owner and request:
            receiver = owner.id
            chat_url = reverse('chat:chat_api', args=[receiver])
            return request.build_absolute_uri(chat_url)
        return None


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['title', 'slug']


class CategorySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(read_only=True)
    detail_edit_url = serializers.HyperlinkedIdentityField(
        view_name="store:category_detail_update",
        lookup_field='pk'
    )
    
    class Meta:
        model = Category
        fields = ["store", "title", "slug", "products", "detail_edit_url"]
        
    def get_products(self, obj):
        my_category = obj
        my_products = my_category.products.all()
        return ProductsInlineSerializer(my_products, many=True, context=self.context).data


    
class ProductSerializer(serializers.ModelSerializer):
    # detail_edit_url = serializers.HyperlinkedIdentityField(
    #     view_name="store:product_detail_update",
    #     lookup_field='pk'
    # )

    class Meta:
        model = Product
        fields = ["id",'category', 'title', "slug", "image", "description", "price", "stock", "available", ]
        # "detail_edit_url"
        


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(source="product_set")
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


