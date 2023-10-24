from rest_framework import permissions
from accounts.models import Profile

class IsSellerIsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user is a seller and the owner of the store associated with the product
        store_id = request.data.get('store')  # Assuming 'store' is the store field in the request data
        profile = Profile.objects.get(user=request.user)
        if store_id and request.user.store_set.filter(id=store_id).exists() and profile.is_seller:
            return True

        return False



class isSeller(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        profile = Profile.objects.get(user=user)
        return profile.is_seller

class isBuyer(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        profile = Profile.objects.get(user=user)
        return profile.is_buyer
