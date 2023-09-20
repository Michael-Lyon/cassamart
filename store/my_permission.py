from rest_framework import permissions

class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user is a seller and the owner of the store associated with the product
        store_id = request.data.get('store')  # Assuming 'store' is the store field in the request data
        if store_id and request.user.store_set.filter(id=store_id).exists() and request.user.is_seller:
            return True

        return False

