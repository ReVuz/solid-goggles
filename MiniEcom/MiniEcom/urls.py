"""
URL configuration for MiniEcom project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include all shop app URLs at the root level
    path('', include('shop.urls')),
]
