from django.contrib import admin
from .models import Customer, Product, Order, OrderItem, Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin view for Cart – shows owner, item count, and total price."""
    list_display = ('user', 'total_items', 'total_price', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('user__username',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin view for CartItem – shows cart owner, product, quantity, and subtotal."""
    list_display = ('get_user', 'product', 'quantity', 'subtotal', 'added_at')
    list_filter = ('product',)
    search_fields = ('cart__user__username', 'product__name')

    @admin.display(description='User')
    def get_user(self, obj):
        return obj.cart.user.username


# Register the remaining models
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
