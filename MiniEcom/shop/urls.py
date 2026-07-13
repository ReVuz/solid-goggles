"""
shop/urls.py
============
URL configuration for the shop app.
Maps URL paths to their corresponding Function-Based Views.
"""

from django.urls import path
from . import views

urlpatterns = [
    # --- Authentication ---
    path('login/',    views.login_view,    name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/',   views.logout_view,   name='logout'),

    # --- Products ---
    path('',                        views.product_list,   name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),

    # --- Cart ---
    path('cart/',                            views.view_cart,       name='view_cart'),
    path('cart/add/<int:product_id>/',       views.add_to_cart,     name='add_to_cart'),
    path('cart/update/<int:item_id>/',       views.update_cart,     name='update_cart'),
    path('cart/remove/<int:item_id>/',       views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/',                      views.clear_cart,      name='clear_cart'),
]
