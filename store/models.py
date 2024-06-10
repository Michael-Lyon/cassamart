from django.contrib.auth.models import User
from django.db import models
from django.db.models import OuterRef, Subquery

from accounts.models import Address, Profile
from payment.models import BankDetail


class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='categories/',
                            default="/media/default.png")

    class Meta:
        ordering = ['title']
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title


class Store(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_store")
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='stores/', default="/media/default.png")
    class Meta:
        ordering = ['title']
        verbose_name = "store"
        verbose_name_plural = "stores"

    def total_products(self):
        return self.products.count()

    def __str__(self):
        return self.title


class Image(models.Model):
    image = models.ImageField(
        upload_to='store/products/', default="/media/default.png")

    def __str__(self):
        return f"Image {self.id}"

class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    store = models.ForeignKey(Store, related_name="products", on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, db_index=True)
    images = models.ManyToManyField(Image, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=1)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='CartItem')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart {self.pk} {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    received = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cart} - {self.product}"


class Checkout(models.Model): # ORDER
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', "Paid"),
        ("not-paid", "Not Paid"),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="not-paid")
    received_status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    reference = models.CharField(max_length=200, blank=True, null=True)
    delivery_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Checkout {self.pk}"

    class Meta:
        ordering = ['-created']


class Discount(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, blank=True, null=True)
    valid = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self) -> str:
        return f"{self.user} is to pay {self.amount} on {self.product} from {self.product.store}"



class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.username}\'s wishlist item: {self.product.title}'


class Wallet(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    # bank_name


class CanceledCheckout(models.Model):
    checkout = models.OneToOneField(
        Checkout, on_delete=models.CASCADE, related_name='canceled_checkout')
    cancel_reason = models.TextField()
    canceled_at = models.DateTimeField(auto_now_add=True)
    refund_bank_details = models.ForeignKey(
        BankDetail, on_delete=models.SET_NULL, null=True, blank=True)


    def get_unique_store_owners(self) -> list[str]:
        # Get the distinct store owners for the products in the checkout
        store_owners = User.objects.filter(
            my_store__products__checkouts=OuterRef('pk'),
            is_seller=True
        ).distinct()

        # Get the FCM tokens from the associated Profile instances
        fcm_tokens = Profile.objects.filter(
            user__in=Subquery(store_owners.values('id'))
        ).values_list('fcm_token', flat=True)

        # Convert the queryset to a list
        return list(fcm_tokens)

    def __str__(self):
        return f'Canceled Checkout: {self.checkout.id}'
