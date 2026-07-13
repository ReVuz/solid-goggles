# MiniEcom - Django E-Commerce Shopping Cart Project

MiniEcom is a simplified, database-backed e-commerce shopping cart application built using **Django** (Function-Based Views) and standard **HTML/CSS** custom-styled to perfectly match the official **Django Admin** styling. It is designed for educational/assignment purposes with clean, readable code and zero bloated frontend frameworks.

---

## Table of Contents
1. [Tech Stack](#tech-stack)
2. [Project Structure](#project-structure)
3. [Features & Functionalities](#features--functionalities)
4. [Installation & Setup](#installation--setup)
5. [How to Run](#how-to-run)
6. [Demo & Testing Credentials](#demo--testing-credentials)

---

## Tech Stack
* **Framework**: Django 5.2.15
* **Language**: Python 3
* **Database**: SQLite (default file-backed DB)
* **Frontend**: Pure HTML5 and CSS3 styled to look exactly like the **Django Admin** interface (utilizing the Classic Slate/Teal color theme).

---

## Project Structure

```text
new-task/
├── .gitignore               # Excludes files like venv, db.sqlite3, and bytecode from git
├── README.md                # This project guide file
└── MiniEcom/                # Django project root
    ├── manage.py            # Django command-line tool
    ├── requirements.txt     # Python dependency list
    ├── populate.py          # Primary DB seeder script (sets up admin & basic shop products)
    ├── populate_more.py     # Secondary DB seeder script (adds more dummy products & customer orders)
    ├── MiniEcom/            # Project configuration folder
    │   ├── settings.py      # App configurations, templates setup, database, and auth settings
    │   └── urls.py          # Master routing pointing root URLs to shop app urls
    └── shop/                # Main shop application folder
        ├── admin.py         # Registers shop models in Django Admin interface
        ├── models.py        # Database models (Customer, Product, Order, Cart, CartItem, etc.)
        ├── urls.py          # Shop-specific view endpoints (products, login, cart actions)
        ├── views.py         # Function-Based Views (FBVs) containing core business logic
        └── templates/shop/  # Plain HTML template files
            ├── base.html            # Main site frame layout & Django Admin aesthetic style definitions
            ├── product_list.html    # Product catalog table (with inline add to cart forms)
            ├── product_detail.html  # Detailed product specs & inventory info
            ├── cart.html            # Shopping cart overview table with update/remove fields
            ├── login.html           # Simple, centered login form layout
            └── register.html        # Simple, centered account registration layout
```

---

## Features & Functionalities

### 1. Database-Backed Cart System
Unlike session-based carts, this application uses a persistent **database-backed cart model** linked to the Django `User` model. This ensures a user's shopping cart persists across logins, devices, and sessions.
* **`Cart` Model** (`shop/models.py`): Owned by a single authenticated User. Includes custom properties:
  * `total_price`: Computes the sum of all item subtotals (`price × quantity`).
  * `total_items`: Computes the total quantity of all items in the cart.
* **`CartItem` Model** (`shop/models.py`): Maps a unique pair of `Cart` and `Product`. Enforces uniqueness constraints (`unique_together`) at the database level to prevent duplicate lines.

### 2. User Authentication & Security
* **Login & Registration** (`shop/views.py` -> `login_view`, `register_view`): Handles Django authentication, creates user sessions, and redirects user safely.
* **BOLA Protection** (Broken Object Level Authorization): The views ensure users can only see and manipulate their own cart items. Cart operations fetch objects via `request.user.cart.items.filter(...)` to prevent users from modifying or viewing other users' items by guessing ID parameters in URLs.
* **Out-of-Stock/Inventory Validation**: Every add/update request checks the current available stock on `Product` and throws a friendly validation alert if requested quantities exceed stock.

### 3. Folder/File Breakdown of Functionalities

| Functionality | View / Method | Location | Template File | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Catalog Listing** | `product_list` | `shop/views.py` | `product_list.html` | Displays all products in the database as a Django Admin-style list table. |
| **Product Detail** | `product_detail` | `shop/views.py` | `product_detail.html` | Displays a detailed view of a product and lets authenticated users select a quantity to add. |
| **Add to Cart** | `add_to_cart` | `shop/views.py` | — (POST redirect) | Appends a product to the user's cart. If the product is already in the cart, increments its quantity. |
| **View Cart** | `view_cart` | `shop/views.py` | `cart.html` | Shows the user's cart items, sub-totals, and grand total. |
| **Update Quantity** | `update_cart` | `shop/views.py` | — (POST redirect) | Updates the quantity of a specific item inside the cart, validating against available stock. |
| **Remove Item** | `remove_from_cart` | `shop/views.py` | — (POST redirect) | Deletes a single item row from the cart. |
| **Clear Cart** | `clear_cart` | `shop/views.py` | — (POST redirect) | Deletes all item rows belonging to the user's cart. |
| **Registration** | `register_view` | `shop/views.py` | `register.html` | Registers a new user. |
| **Login** | `login_view` | `shop/views.py` | `login.html` | Authenticats users and maps them to their session. |
| **Logout** | `logout_view` | `shop/views.py` | — (POST redirect) | Destroys the user session. |

---

## Installation & Setup

1. **Clone or navigate** to the project workspace directory:
   ```bash
   cd /home/hp/Documents/new-task
   ```

2. **Create a Python Virtual Environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment**:
   * **Linux/macOS**:
     ```bash
     source venv/bin/activate
     ```
   * **Windows**:
     ```cmd
     venv\Scripts\activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r MiniEcom/requirements.txt
   ```

5. **Run Database Migrations**:
   This sets up the SQLite database schema including Django's authentication tables and the custom shop models:
   ```bash
   cd MiniEcom
   python manage.py migrate
   ```

6. **Seed Database with Demo Data**:
   Populate the store with products, customers, and superuser accounts using the helper scripts:
   ```bash
   python populate.py
   python populate_more.py
   ```

---

## How to Run

Start the Django local development server:
```bash
python manage.py runserver
```

You can now open your browser and navigate to:
* Main Shop URL: **`http://127.0.0.1:8000/`**
* Django Site Administration: **`http://127.0.0.1:8000/admin/`**

---

## Demo & Testing Credentials

Use the following seeded credentials to log in and test all functionalities (or register your own account):

* **Superuser / Admin Login**:
  * **Username**: `admin`
  * **Password**: `admin123`
