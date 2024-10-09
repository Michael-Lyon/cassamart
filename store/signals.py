import time
import hashlib
from django.conf import settings
from cloudinary.uploader import upload
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Image, Category


def generate_signature(params, api_secret):
    """Generate Cloudinary signature manually."""
    signature_data = '&'.join(
        [f"{key}={params[key]}" for key in sorted(params)]) + api_secret
    return hashlib.sha1(signature_data.encode('utf-8')).hexdigest()


@receiver(post_save, sender=Image)
def upload_image_to_cloudinary(sender, instance, **kwargs):
    if not instance.image or "res.cloudinary.com" in instance.image.url:
        return

    timestamp = int(time.time())
    params = {
        'timestamp': timestamp,
        'public_id': f"image_{instance.id}"
    }

    # Generate signature using API secret
    api_secret = settings.CLOUDINARY_STORAGE['API_SECRET']  # Fetch securely
    signature = generate_signature(params, api_secret)

    # Upload to Cloudinary
    upload_result = upload(
        instance.image.path,
        public_id=params['public_id'],
        api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
        timestamp=timestamp,
        signature=signature
    )

    if upload_result.get("url"):
        instance.image = upload_result['url']
        instance.save()  # Save the new image URL in the model


@receiver(post_save, sender=Category)
def upload_category_image_to_cloudinary(sender, instance, **kwargs):
    if not instance.image or "res.cloudinary.com" in instance.image.url:
        return

    timestamp = int(time.time())
    params = {
        'timestamp': timestamp,
        'public_id': f"category_{instance.id}"
    }

    # Generate signature using API secret
    api_secret = settings.CLOUDINARY_STORAGE['API_SECRET']
    signature = generate_signature(params, api_secret)

    # Upload to Cloudinary
    upload_result = upload(
        instance.image.path,
        public_id=params['public_id'],
        api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
        timestamp=timestamp,
        signature=signature
    )

    if upload_result.get("url"):
        instance.image = upload_result['url']
        instance.save()  # Save the new image URL in the model
