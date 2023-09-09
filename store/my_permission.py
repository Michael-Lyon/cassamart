from rest_framework import permissions

class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a seller (you need to define your logic for this)
        return hasattr(request.user, "sellerprofile")  # Replace with your logic to determine if the user is a seller
