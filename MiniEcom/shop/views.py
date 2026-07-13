"""
shop/views.py
=============
Function-Based Views for the MiniEcom cart module.

All cart-related views require authentication (@login_required).
Cart data is stored in the database (NOT session-based).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError

from .models import Product, Cart, CartItem


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _get_or_create_cart(user):
    """Return (or lazily create) the Cart row for the given user."""
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


# ---------------------------------------------------------------------------
# Authentication views
# ---------------------------------------------------------------------------

def login_view(request):
    """
    Display the login form (GET) and authenticate the user (POST).
    Redirects to the product listing on success.
    """
    if request.user.is_authenticated:
        return redirect('product_list')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            error = "Both username and password are required."
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Honour 'next' param if present
                next_url = request.GET.get('next', 'product_list')
                return redirect(next_url)
            else:
                error = "Invalid username or password."

    return render(request, 'shop/login.html', {'error': error})


def register_view(request):
    """
    Display the registration form (GET) and create a new User (POST).
    Automatically logs in the new user after registration.
    """
    if request.user.is_authenticated:
        return redirect('product_list')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not username or not password:
            error = "Username and password are required."
        elif password != password2:
            error = "Passwords do not match."
        elif User.objects.filter(username=username).exists():
            error = "That username is already taken."
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            messages.success(request, f"Welcome, {username}! Your account has been created.")
            return redirect('product_list')

    return render(request, 'shop/register.html', {'error': error})


def logout_view(request):
    """Log out the current user and redirect to the login page."""
    if request.method == 'POST':
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect('login')


# ---------------------------------------------------------------------------
# Product views
# ---------------------------------------------------------------------------

def product_list(request):
    """
    Display all available products.
    Accessible to both anonymous and authenticated users (browsing).
    """
    products = Product.objects.all().order_by('name')

    # Provide cart item count for the nav badge (authenticated users only)
    cart_item_count = 0
    if request.user.is_authenticated:
        try:
            cart_item_count = request.user.cart.total_items
        except Cart.DoesNotExist:
            pass

    context = {
        'products': products,
        'cart_item_count': cart_item_count,
    }
    return render(request, 'shop/product_list.html', context)


def product_detail(request, product_id):
    """
    Display details for a single product.
    Includes an 'Add to Cart' form with quantity input.
    """
    product = get_object_or_404(Product, pk=product_id)

    cart_item_count = 0
    if request.user.is_authenticated:
        try:
            cart_item_count = request.user.cart.total_items
        except Cart.DoesNotExist:
            pass

    context = {
        'product': product,
        'cart_item_count': cart_item_count,
    }
    return render(request, 'shop/product_detail.html', context)


# ---------------------------------------------------------------------------
# Cart views – all require login
# ---------------------------------------------------------------------------

@login_required
def view_cart(request):
    """
    Display the current user's cart:
    - Lists every CartItem with quantity, unit price, and subtotal
    - Shows the grand total
    """
    cart = _get_or_create_cart(request.user)
    # Pre-fetch related product data to avoid N+1 queries
    items = cart.items.select_related('product').all()

    context = {
        'cart': cart,
        'items': items,
        'cart_item_count': cart.total_items,
    }
    return render(request, 'shop/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    """
    Add a product to the cart (POST only).

    Validation rules:
    - Product must exist (404 otherwise).
    - Quantity must be a positive integer (≥ 1).
    - If the product is already in the cart, its quantity is incremented.
    """
    if request.method != 'POST':
        # Only POST is allowed for this operation
        messages.error(request, "Invalid request method.")
        return redirect('product_list')

    # --- Validate product ---
    product = get_object_or_404(Product, pk=product_id)

    # --- Validate quantity ---
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity. Please enter a whole number.")
        return redirect('product_detail', product_id=product_id)

    if quantity < 1:
        messages.error(request, "Quantity must be at least 1.")
        return redirect('product_detail', product_id=product_id)

    # --- Check stock availability ---
    if quantity > product.stock:
        messages.error(
            request,
            f"Only {product.stock} unit(s) of '{product.name}' are available."
        )
        return redirect('product_detail', product_id=product_id)

    # --- Get or create the user's cart ---
    cart = _get_or_create_cart(request.user)

    # --- Add or increment cart item ---
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity},
    )

    if not created:
        # Product already in cart – increment quantity
        new_qty = cart_item.quantity + quantity
        if new_qty > product.stock:
            messages.error(
                request,
                f"Cannot add {quantity} more – only {product.stock - cart_item.quantity} "
                f"additional unit(s) of '{product.name}' are available."
            )
            return redirect('product_detail', product_id=product_id)
        cart_item.quantity = new_qty
        cart_item.save()
        messages.success(
            request,
            f"Updated '{product.name}' quantity to {cart_item.quantity} in your cart."
        )
    else:
        messages.success(request, f"'{product.name}' added to your cart.")

    return redirect('view_cart')


@login_required
def update_cart(request, item_id):
    """
    Update the quantity of a specific CartItem (POST only).

    Validation rules:
    - CartItem must belong to the requesting user's cart.
    - New quantity must be a positive integer (≥ 1).
    - Setting quantity to 0 is treated as a remove request.
    """
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('view_cart')

    cart = _get_or_create_cart(request.user)
    # Ensure the item belongs to THIS user's cart (prevents cross-user tampering)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    # --- Validate new quantity ---
    try:
        new_quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity. Please enter a whole number.")
        return redirect('view_cart')

    if new_quantity < 0:
        messages.error(request, "Quantity cannot be negative.")
        return redirect('view_cart')

    if new_quantity == 0:
        # Treat zero quantity as removal
        product_name = cart_item.product.name
        cart_item.delete()
        messages.info(request, f"'{product_name}' removed from your cart.")
        return redirect('view_cart')

    # --- Check stock availability ---
    if new_quantity > cart_item.product.stock:
        messages.error(
            request,
            f"Only {cart_item.product.stock} unit(s) of '{cart_item.product.name}' are in stock."
        )
        return redirect('view_cart')

    cart_item.quantity = new_quantity
    cart_item.save()
    messages.success(
        request,
        f"'{cart_item.product.name}' quantity updated to {new_quantity}."
    )
    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    """
    Remove a single CartItem from the cart (POST only).
    The item must belong to the requesting user's cart.
    """
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('view_cart')

    cart = _get_or_create_cart(request.user)
    # Ownership check: item must belong to the current user's cart
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    product_name = cart_item.product.name
    cart_item.delete()
    messages.info(request, f"'{product_name}' has been removed from your cart.")
    return redirect('view_cart')


@login_required
def clear_cart(request):
    """
    Remove ALL items from the user's cart in one action (POST only).
    """
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('view_cart')

    cart = _get_or_create_cart(request.user)
    count = cart.items.count()
    cart.items.all().delete()
    messages.info(request, f"Your cart has been cleared ({count} item(s) removed).")
    return redirect('view_cart')
