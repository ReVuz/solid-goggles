"""
shop/ai_service.py
==================
AI service layer for the MiniEcom shop.

Provides two core functions:
  - generate_description(name, category) → str
  - predict_price(name, category, description) → Decimal | None

Both use the Google Gemini API via the `google-genai` SDK (gemini-2.0-flash).
The API key is read from Django settings (GEMINI_API_KEY).
"""

import re
import logging
from decimal import Decimal, InvalidOperation

from google import genai
from django.conf import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_client() -> genai.Client:
    """Build and return a configured Gemini Client."""
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set in Django settings. "
            "Add it to settings.py or export it as an environment variable."
        )
    return genai.Client(api_key=api_key)


def _safe_generate(prompt: str) -> str:
    """
    Send a single-turn prompt to Gemini and return the text response.
    Returns '' if the API call fails (logs the error).
    """
    try:
        client = _get_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as exc:
        logger.error("Gemini API call failed: %s", exc)
        return ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_description(name: str, category: str) -> str:
    """
    Generate a professional product description for the given name and category.

    Args:
        name:     The product name (e.g. "Wireless Noise-Cancelling Headphones").
        category: The product category (e.g. "Electronics").

    Returns:
        A 2–3 sentence marketing description, or '' on failure.
    """
    prompt = (
        "You are a professional e-commerce copywriter.\n"
        "Write a compelling, 2-to-3 sentence product description for the item below.\n"
        "Be specific, highlight key benefits, and use persuasive language.\n"
        "Do NOT include the price or any HTML tags.\n\n"
        f"Product Name : {name}\n"
        f"Category     : {category}\n\n"
        "Product Description:"
    )
    description = _safe_generate(prompt)
    logger.info("AI description generated for '%s': %s…", name, description[:60])
    return description


def predict_price(name: str, category: str, description: str = "") -> Decimal | None:
    """
    Predict a realistic retail price (INR) for the given product.

    Args:
        name:        The product name.
        category:    The product category.
        description: Optional description to improve accuracy.

    Returns:
        A Decimal price value quantized to 2 decimal places, or None on failure.
    """
    desc_clause = f"\nDescription : {description}" if description else ""
    prompt = (
        "You are an expert pricing analyst for an Indian e-commerce platform.\n"
        "Predict a realistic retail price in Indian Rupees (INR) for the product below.\n"
        "Base your estimate on typical prices found on Amazon India or Flipkart.\n"
        "Reply with ONLY a single number (no ₹ symbol, no commas, no extra text).\n\n"
        f"Product Name : {name}\n"
        f"Category     : {category}"
        f"{desc_clause}\n\n"
        "Predicted Price (INR):"
    )
    raw = _safe_generate(prompt)

    # Extract the first numeric value (handles "1299.00", "1,299", "≈1500" etc.)
    match = re.search(r"[\d,]+\.?\d*", raw)
    if not match:
        logger.warning("Could not parse price from AI response: '%s'", raw)
        return None

    numeric_str = match.group().replace(",", "")
    try:
        price = Decimal(numeric_str).quantize(Decimal("0.01"))
        logger.info("AI predicted price for '%s': ₹%s", name, price)
        return price
    except InvalidOperation:
        logger.warning("Invalid Decimal from AI price string: '%s'", numeric_str)
        return None
