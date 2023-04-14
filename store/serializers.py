from rest_framework import serializers
from .models import Store, Category, Product

class CategoryInlineSerializer(serializers.Serializer):
    owner = serializers.CharField(read_only=True )
    title = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    products = serializers.SerializerMethodField(read_only=True)
    detail_edit_url = serializers.HyperlinkedIdentityField(
        view_name = "store:category_detail_update",
        lookup_field = 'pk'
    )
    
    def get_products(self, obj):
        my_category = obj
        my_products = my_category.products.all()
        return ProductsInlineSerializer(my_products, many=True, context=self.context).data

class ProductsInlineSerializer(serializers.Serializer):
    
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
    class Meta:
        model = Store
        fields = ['owner', "title", "slug","categories" ]
    
    def get_categories(self, obj):
        store = obj
        my_categories = store.categories.all()
        return CategoryInlineSerializer(my_categories, many=True, context=self.context).data
    
    


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
        read_only_fields = ['store']
        fields = [ "title", "slug", "products", "detail_edit_url"]
        
    def get_products(self, obj):
        my_category = obj
        my_products = my_category.products.all()
        return ProductsInlineSerializer(my_products, many=True, context=self.context).data


    
class ProductSerializer(serializers.ModelSerializer):
    detail_edit_url = serializers.HyperlinkedIdentityField(
        view_name="store:product_detail_update",
        lookup_field='pk'
    )
    
    class Meta:
        model = Product
        fields = ['category', 'title', "slug", "image", "description", "price", "stock", "available", "detail_edit_url"]
    