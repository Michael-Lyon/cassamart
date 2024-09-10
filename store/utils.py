import base64
import json
import uuid

from django.core.mail import send_mail
from django.contrib.auth.models import User

from casamart.settings import EMAIL_HOST_USER as SENDER
from python_paystack.managers import TransactionsManager
from store.models import Cart


def check_payment(reference: str) -> str:
    #  print((TransactionsManager().verify_transaction(
            # transaction_reference=response["reference"])).to_json())
    try:
        transaction_manager = TransactionsManager()
        transaction = transaction_manager.verify_transaction(transaction_reference=reference)
        if isinstance(transaction, str):
            return transaction
        transaction = json.loads(transaction.to_json())
        print(transaction)
        return transaction['status']
    except Exception as e:
        return str(e)


def send_wallet_mail(owners: dict):
    for user, amount in owners.items():
        message = f"Hello {user}\nYour wallet has been topped with NGN{amount}"
        send_mail(subject="Cassamart Wallet Top-Up",message=message,
                from_email=SENDER, recipient_list=[user.email], fail_silently=False)


def send_order_mail(cart: Cart):
    owners = {}
    for cart_item in cart.cartitem_set.all():
        user = cart_item.product.store.owner
        product = cart_item.product
        owners.setdefault(user, [])
        owners[user].append(product)
    for user, products in owners.items():  # Use items() to iterate over key-value pairs
        message = f"Hello {user.username}\nYou have received a new order for {', '.join(product.title for product in products)}."
        send_mail(subject="Cassamart New Order", message=message,
                from_email=SENDER, recipient_list=[user.email], fail_silently=False)


def send_buyer_order_mail(cart: Cart, user: User):
    # for user, products in owners.items():  # Use items() to iterate over key-value pairs
    message = f"Hello {user.username}\nYou have placed an order for {', '.join(product.product.title for product in cart.cartitem_set.all())}."
    send_mail(subject="Cassamart New Order", message=message,
            from_email=SENDER, recipient_list=[user.email], fail_silently=False)




def generate_discount_id():
    # Generate a UUID
    unique_id = uuid.uuid4()

    # Convert UUID to bytes
    uuid_bytes = unique_id.bytes

    # Encode the UUID bytes using base64
    base64_encoded = base64.b64encode(uuid_bytes)

    # Take the first 6 characters
    discount_id = base64_encoded[:10].decode()

    return str(discount_id)
