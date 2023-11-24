from django.contrib import admin

from .models import Cart, CartItem, Category, Checkout, Product, ProductImage, Store

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Checkout)
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'slug']
    prepopulated_fields = {'slug': ('title', )}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


class ProductImageInline(admin.StackedInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["category", "get_store", "get_owner", 'title', 'slug', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline]

    def get_store(self, obj):
        return obj.store

    def get_owner(self, obj):
        return obj.store.owner

    get_owner.short_description = 'Owner'
    get_store.short_description = 'Store'
