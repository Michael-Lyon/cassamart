from django.db import models
from django.contrib.auth.models import User



class Store(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_store")
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['title']
        verbose_name = "store"
        verbose_name_plural = "stores"
    
    def __str__(self):
        return self.title



class Category(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="categories")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['title']
        verbose_name = "category"
        verbose_name_plural = "categories"
    
    def __str__(self):
        return self.title


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='media/')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=1)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        ordering = ('title',)
        index_together = (('id', 'slug'))

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

    def __str__(self):
        return f"{self.cart} - {self.product}"


class Checkout(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', "Paid"),
        ("not-paid", "Not Paid")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.OneToOneField('Cart', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="not-paid")
    received_status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    reference = models.CharField(max_length=200, blank=True, null=True)
    delivery_address = models.CharField(max_length=1000, null=True, blank=True )

    def __str__(self):
        return f"Checkout {self.pk}"


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.title
