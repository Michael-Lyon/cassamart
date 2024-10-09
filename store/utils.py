from cloudinary.exceptions import Error
from django.conf import settings
import hashlib
import os
import time
import cloudinary.uploader
import cloudinary
import base64
import json
import uuid
import requests

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


# Ensure CLOUDINARY_STORAGE is defined correctly
CLOUDINARY_API_SECRET = settings.CLOUDINARY_STORAGE['API_SECRET']


# def generate_signature(params, api_secret):
#     # Sort params and generate signature string
#     sorted_params = sorted(params.items())
#     string_to_sign = '&'.join(f"{k}={v}" for k, v in sorted_params)
#     # Hash the string using SHA1 and API secret
#     return hashlib.sha1((string_to_sign + api_secret).encode('utf-8')).hexdigest()


# def upload_to_cloudinary(sender, instance, **kwargs):
#     """
#     Signal function to handle image upload via Cloudinary
#     """

#     # Generate the current timestamp
#     timestamp = int(time.time())

#     # Parameters to sign (you can add more params if needed)
#     params = {
#         'timestamp': timestamp
#     }

#     # Generate signature using the helper function
#     signature = generate_signature(params, CLOUDINARY_API_SECRET)

#     # URL for uploading to Cloudinary (modify based on the endpoint)
#     cloudinary_url = f"https://api.cloudinary.com/v1_1/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/image/upload"

#     # Include your other form data for Cloudinary
#     form_data = {
#         'file': instance.image,  # Assuming 'image' is the file field
#         'api_key': settings.CLOUDINARY_STORAGE['API_KEY'],
#         'timestamp': timestamp,
#         'signature': signature,
#     }

#     # Now, make an HTTP request to upload the file (e.g., using requests or another HTTP client)
#     response = requests.post(cloudinary_url, data=form_data)

#     # Handle response as needed
#     if response.status_code == 200:
#         # Successful upload, maybe update instance with Cloudinary URL
#         instance.image_url = response.json().get('secure_url')
#         instance.save()
#     else:
#         # Handle upload error
#         raise Exception("Cloudinary upload failed.")

# # Connect this signal to your model's save method or wherever necessary


def generate_signature(params, api_secret):
    """
    Generate Cloudinary signature manually by hashing the params with API secret.
    """
    # Create the string to sign in the correct format
    signature_string = '&'.join(
        [f"{k}={v}" for k, v in sorted(params.items())])
    signature_string += api_secret

    # Hash the signature string using SHA-1
    return hashlib.sha1(signature_string.encode('utf-8')).hexdigest()


def upload_image_to_cloudinary(image_file, public_id=None):
    """
    Upload an image file to Cloudinary and return the secure URL.
    :param image_file: The file object of the image to upload.
    :param public_id: An optional public ID for the Cloudinary resource.
    :return: The secure URL of the uploaded image or None if failed.
    """
    try:
        # Generate a timestamp
        timestamp = int(time.time())

        # Parameters for signature generation
        params = {
            'timestamp': timestamp,
        }

        if public_id:
            params['public_id'] = public_id

        # Generate the signature using the Cloudinary API secret
        api_secret = settings.CLOUDINARY_STORAGE['API_SECRET']
        signature = generate_signature(params, api_secret)

        # Now perform the upload to Cloudinary, passing the signature
        upload_result = cloudinary.uploader.upload(
            image_file,
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=api_secret,
            public_id=public_id,
            timestamp=timestamp,
            signature=signature
        )

        # Return the secure URL if the upload was successful
        return upload_result.get('secure_url')

    except Error as e:
        # Handle Cloudinary-specific errors and log them as needed
        print(f"Cloudinary upload failed: {e}")
        return None
