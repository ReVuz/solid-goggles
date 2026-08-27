from django.db import models
from django.contrib.auth.models import User


# ---------------------------------------------------------------------------
# Existing shop models (Customer, Product, Order, OrderItem)
# ---------------------------------------------------------------------------

class Customer(models.Model):
    """Represents a shop customer profile (separate from auth User)."""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """A product available for purchase in the store."""
    name = models.CharField(max_length=150)
    # Category used for AI description/price prompts and for filtering
    category = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    # Optional image URL for product card display
    image_url = models.URLField(blank=True, default='')

    def __str__(self):
        return self.name


class Order(models.Model):
    """A confirmed purchase order placed by a customer."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.customer.name}"


class OrderItem(models.Model):
    """A single line item within an Order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"


# ---------------------------------------------------------------------------
# Cart models – database-backed, one cart per authenticated user
# ---------------------------------------------------------------------------

class Cart(models.Model):
    """
    A shopping cart owned by a single authenticated user.
    Created automatically the first time a user adds an item.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_price(self):
        """Grand total: sum of (price × quantity) for every item in the cart."""
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        """Total number of individual product units in the cart."""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """
    A single product line in a Cart.
    Each (cart, product) pair is unique – adding the same product again
    increments the existing item's quantity instead of creating a duplicate.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Enforce one row per (cart, product) combination at the DB level
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} × {self.product.name} in {self.cart}"

    @property
    def subtotal(self):
        """Price × quantity for this line item."""
        return self.product.price * self.quantity
