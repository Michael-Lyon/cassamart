from .models import CanceledCheckout
from django.contrib import admin

from .models import Cart, CartItem, Category, Checkout, Product, Store, WishlistItem

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Checkout)
admin.site.register(WishlistItem)
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
    list_display = ["category", "get_store", "get_owner", 'title', 'slug', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('title',)}

    def get_store(self, obj):
        return obj.store

    def get_owner(self, obj):
        return obj.store.owner

    get_owner.short_description = 'Owner'
    get_store.short_description = 'Store'


@admin.register(CanceledCheckout)
class CanceledCheckoutAdmin(admin.ModelAdmin):
    list_display = ('checkout', 'cancel_reason',
                    'canceled_at', 'refund_bank_details')
    list_filter = ('canceled_at',)
    search_fields = ('checkout__id', 'cancel_reason')
    readonly_fields = ('checkout', 'canceled_at')
    fieldsets = (
        (None, {
            'fields': ('checkout', 'canceled_at')
        }),
        ('Cancellation Details', {
            'fields': ('cancel_reason', 'refund_bank_details')
        }),
        ('Store Owners', {
            'fields': ('get_unique_store_owners',)
        }),
    )

    def get_unique_store_owners(self, obj):
        return ", ".join(obj.get_unique_store_owners())

    get_unique_store_owners.short_description = 'Store Owners (FCM Tokens)'
