from django.contrib import admin

from .models import Address, Profile

admin.site.register(Profile)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'latitude', 'longitude')
    search_fields = ('user__username', 'address')
    list_filter = ('user',)

    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Address Info', {
            'fields': ('address', 'latitude', 'longitude')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['user']
        return []

    def save_model(self, request, obj, form, change):
        # Automatically set the user based on the currently logged-in user
        if not obj.user:
            obj.user = request.user
        obj.save()


# admin.site.site_header = 'Your Site Admin'
# admin.site.site_title = 'Your Site Admin'
# admin.site.index_title = 'Site Administration'
