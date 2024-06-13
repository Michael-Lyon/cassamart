from json import JSONDecodeError
import traceback
from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, mixins, serializers, status
from accounts.models import Profile, Wallet
from casamart.notification_sender import send_push_notification
from payment.models import BankDetail, Transaction
from payment.serializers import BankDetailSerializer
from rest_framework.views import APIView
# Create your views here.
from python_paystack.managers import Utils
from rest_framework.response import Response
from casamart.utils import create_response
from store.models import Cart, CartItem, Checkout
from store import utils
from rest_framework import status as stat
from .payment_manager import PaystackManager
from django.db import transaction


bank_utils = Utils()

class BankDetailView(generics.ListCreateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = BankDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return BankDetail.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = create_response(
            data=response.data['results'],
            message="Created/Retrieved Successfully",
            status="success",
        )
        return Response(response.data)


class GetBanksView(APIView):
    def get(self, request):
        response_data = {
            "data": bank_utils.get_banks(),
            "errors": None,
            "status": "failed",
            "message": "Banks retrieved successfully",
            "pagination": {
                "count": None,
                "next": None,
                "previous": None,
            }
        }
        return Response(response_data)


class AccountNumberResolver(APIView):
    """
    get:
    Resolve an account number.

    This endpoint resolves an account number given the account number and bank code.
    It returns the details of the account associated with the account number.

    **Parameters:**
    - account_number: The account number to resolve.
    - bank_code: The code of the bank where the account is held.
    """

    def get(self, request, *args, **kwargs):
        account_number = request.query_params.get('account_number', None)
        bank_code = request.query_params.get('bank_code', None)

        if account_number and bank_code:
            try:
                data = create_response(data=bank_utils.resolve_account_number(account_number=account_number, bank_code=bank_code), message="Bank resolved successfully", status="success")
                return Response(data)
            except JSONDecodeError:
                return Response(create_response(message="Something went wrong with the network try again please"))
            except Exception as a:
                print(a)
                traceback.print_exc()
                return Response(create_response(message="Something went wrong. We're on it."))
        else:
            return Response(create_response(message="Bank not found"))


class GoodsReceived(APIView):
    """
    **POST**:
    Indicate a goods has been received.

    This endpoint through post gets a product id which indicates that the user has received the product and then makes payment to the owner of the product

    **PayLoad:**
    - product_id: The product id to resolve.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        user = request.user

        product_id = data.get('product_id')
        if not product_id:
            return Response(create_response(message="Product ID is required"), status=status.HTTP_400_BAD_REQUEST)

        try:
            product_id = int(product_id)
        except ValueError:
            return Response(create_response(message="Invalid Product ID"), status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.filter(user=user).order_by('-created').first()
            cart_item = CartItem.objects.get(cart=cart, product__id=product_id)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(create_response(message="Cart or Product not found"), status=status.HTTP_404_NOT_FOUND)

        product = cart_item.product
        price = product.price
        owner = product.store.owner

        manager = PaystackManager()
        bank_detail = BankDetail.objects.filter(user=owner).first()
        if not bank_detail:
            return Response(create_response(message="No bank detail found"), status=status.HTTP_404_NOT_FOUND)

        if not bank_detail.recipient_code:
            is_recipient_created = manager.create_transfer_recipient(
                detail=bank_detail)
            if not is_recipient_created:
                return Response(create_response(message="Payment Failed, Please try again later"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        with transaction.atomic():
            if self.transfer_and_create_transaction(manager, bank_detail, price):
                cart_item.received = True
                cart_item.save()
                Checkout.objects.get(cart=cart).check_received_status()
                send_push_notification(Profile.objects.get(
                    user=owner).fcm_token, "Order Received", "Order Received by buyer and payment has been initiated")
                return Response(create_response(message="Payment initiated", status="success"), status=status.HTTP_200_OK)
            return Response(create_response(message="Something went wrong while initiating payment. Please try again later.", status="failed"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def transfer_and_create_transaction(self, manager, detail, amount):
        """Function to initiate transfer and create a transaction instance"""
        transfer_code, status = manager.transfer(detail=detail, amount=amount)
        if transfer_code and status:
            Transaction.objects.create(
                bank_details=detail,
                amount=amount,
                status=status,
                transfer_code=transfer_code
            )
            return True
        return False






        # owners = {}
        # id = data["id"]
        #
        # cart = Cart.objects.get(id=id, user=user)
        # status = data['status']
        # if status:
        #     for cart_item in cart.cartitem_set.all():
        #         product_owner = cart_item.product.category.store.owner
        #         payment_amount = cart_item.product.price * cart_item.quantity
        #         owners.setdefault(product_owner, 0)
        #         owners[product_owner] += payment_amount
        #         # Add each product owner money to thier wallet
        #         created, wallet = Wallet.objects.get_or_create(
        #             user=product_owner)
        #         wallet.amount += payment_amount
        #     # send mails to the onwers of the products that their accounts have been topped
        #     utils.send_wallet_mail(owners)
        #     response_data = {
        #         "data": {"message": "Updated."},
        #         "errors": None,
        #         "status": "success",
        #         "message": "Goods received updated successfully",
        #         "pagination": None
        #     }
        #     return Response(response_data, status=status.HTTP_200_OK)
        # return Response({"message": "Updated."}, status=stat.HTTP_409_CONFLICT)
