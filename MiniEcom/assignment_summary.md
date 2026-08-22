# E-Commerce Cart Module: Assignment Summary & Feedback Report

## 1. Approach
The objective of this assignment was to implement a database-backed Shopping Cart for a Django e-commerce application using Function-Based Views (FBVs). The approach taken was:

*   **Database Design:** Implemented `Cart` and `CartItem` models. The `Cart` has a one-to-one relationship with the Django `User` model, ensuring each authenticated user has a single unique cart. The `CartItem` links the `Cart` to the `Product` with a specific quantity, and includes a `unique_together` constraint to prevent duplicate items for the same product in a single cart.
*   **Function-Based Views (FBVs):** Created clear, distinct FBVs for each cart operation (`view_cart`, `add_to_cart`, `update_cart`, `remove_from_cart`). All views are secured using the `@login_required` decorator.
*   **Robustness & Validation:** Each view includes validations for input data. For example, `add_to_cart` ensures the product exists, the quantity is a positive integer, and there is sufficient stock available. Errors are handled gracefully using Django's `messages` framework.
*   **Data Integrity:** A helper function `_get_or_create_cart` ensures that a cart is dynamically created when a user first attempts to use it, preventing `DoesNotExist` exceptions.

## 2. Challenges
*   **Stock Management Validation:** Implementing logic to ensure users cannot add more items to their cart than are currently available in the product's stock. This required checking both the requested quantity and the existing quantity in the cart.
*   **Preventing Duplicate Cart Items:** Instead of creating a new `CartItem` every time a user clicks "Add to Cart" for the same product, the system was designed to find the existing `CartItem` and increment its quantity. This was achieved efficiently using `get_or_create`.
*   **Data Ownership:** Ensuring that users can only modify their own cart items. In `update_cart` and `remove_from_cart`, the `get_object_or_404` query explicitly filters by both the `item_id` and the user's `cart` to prevent cross-cart modification vulnerabilities.

## 3. Learning Outcomes
*   Deepened understanding of Django ORM relationships, specifically `OneToOneField` for user profiles/carts and `ForeignKey` for line items.
*   Gained practical experience implementing secure, database-backed state management as opposed to relying on session storage.
*   Improved ability to write defensive code in views, handling edge cases like invalid input types, negative quantities, and out-of-stock scenarios.
*   Learned how to effectively use Django's messaging framework to provide immediate, clear feedback to the user after actions like adding or removing items.

---

# Detailed Feedback Report & Scorecard

## Overall Performance
The implementation successfully meets all functional and technical requirements. The code is well-structured, thoroughly commented, and handles edge cases effectively. The choice to use `@property` methods on models for subtotal calculations keeps business logic out of the templates and views, adhering to the "fat models, skinny views" principle.

## Scorecard

| Skill Category | Sub-Components | Expected Proficiency | Actual Proficiency | Feedback |
| :--- | :--- | :--- | :--- | :--- |
| **Model Design** | Django ORM, DB schema | Intermediate | **Advanced** | Excellent use of `OneToOneField`, `related_name`, and `unique_together` constraints. The `@property` methods for dynamic calculations are a strong addition. |
| **Cart Functionality** | CRUD Operations | Intermediate | **Advanced** | All operations (add, update, remove, clear) are implemented correctly. The `get_or_create` logic for incrementing quantities is clean and efficient. |
| **Views & Templates** | Django FBVs, Rendering | Intermediate | **Intermediate** | Views are well-separated by responsibility. Context is passed correctly to templates. |
| **Authentication** | Security, user restrictions | Intermediate | **Intermediate** | `@login_required` is correctly applied. The ownership checks in the update/remove views prevent unauthorized modifications. |
| **Validation** | Invalid quantity/product checks | Beginner | **Intermediate** | Input is cast to integers and checked for negative values. Stock availability is rigorously validated. |
| **Error Handling** | Graceful messages | Beginner | **Intermediate** | Django `messages` are used effectively to communicate success, errors, and informational updates to the user. |
| **Code Organization** | Naming, modularity, comments | Intermediate | **Intermediate** | Code is very readable, with clear docstrings, logical grouping of views, and descriptive variable names. |
