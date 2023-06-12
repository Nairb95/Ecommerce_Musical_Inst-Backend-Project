from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Category(models.Model):
    ACOUSTIC = 'acoustic'
    ELECTRIC = 'electric'
    CATEGORY_CHOICES = [
        (ACOUSTIC, 'Acoustic'),
        (ELECTRIC, 'Electric'),
    ]
    name = models.CharField(max_length=255, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    GUITARS = 'guitars'
    VIOLINS = 'violins'
    PIANOS = 'pianos'
    BASSES = 'basses'
    SYNTHS = 'synths'
    SUBCATEGORY_CHOICES = [
        (GUITARS, 'Guitars'),
        (VIOLINS, 'Violins'),
        (PIANOS, 'Pianos'),
        (BASSES, 'Basses'),
        (SYNTHS, 'Synths'),
    ]
    name = models.CharField(max_length=255, choices=SUBCATEGORY_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')
    brand = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - User {self.user.username}"

    def total_price(self):
        items = self.items.all()
        total = sum(item.product.price * item.quantity for item in items)
        return total

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"Order Item {self.id} - Order {self.order.id}"