from django.contrib import admin
from .models import Product, Category, Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'slug']
    prepopulated_fields = {'slug': ('title', )}
    

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('title',)}
