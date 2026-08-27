"""
shop/forms.py
=============
ModelForm for the AI-powered product creation feature.
"""

from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    """
    ModelForm for creating a new Product.

    The description and price fields are intentionally optional here
    because the view will fill them in via AI if left blank.
    """

    class Meta:
        model = Product
        fields = ["name", "category", "description", "price", "stock", "image_url"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "e.g. Wireless Noise-Cancelling Headphones",
                "id": "id_name",
            }),
            "category": forms.TextInput(attrs={
                "placeholder": "e.g. Electronics",
                "id": "id_category",
            }),
            "description": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Leave blank to let AI generate a description…",
                "id": "id_description",
            }),
            "price": forms.NumberInput(attrs={
                "step": "0.01",
                "min": "0",
                "placeholder": "Leave blank for AI price prediction…",
                "id": "id_price",
            }),
            "stock": forms.NumberInput(attrs={
                "min": "0",
                "placeholder": "e.g. 50",
                "id": "id_stock",
            }),
            "image_url": forms.URLInput(attrs={
                "placeholder": "https://example.com/image.jpg (optional)",
                "id": "id_image_url",
            }),
        }
        labels = {
            "name":      "Product Name *",
            "category":  "Category *",
            "description": "Description (optional – AI will generate if blank)",
            "price":     "Price ₹ (optional – AI will predict if blank)",
            "stock":     "Stock Quantity *",
            "image_url": "Image URL (optional)",
        }

    def clean_price(self):
        """Allow price to be blank; the view will handle AI prediction."""
        return self.cleaned_data.get("price")  # may be None

    def clean_description(self):
        """Strip whitespace; empty string triggers AI generation in the view."""
        return (self.cleaned_data.get("description") or "").strip()
