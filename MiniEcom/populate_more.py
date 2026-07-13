import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MiniEcom.settings')
django.setup()

from shop.models import Customer, Product, Order, OrderItem
import random

def populate_more():
    print("Adding MORE dummy values to the database...")

    # 1. Add more Customers
    customers_data = [
        ("Charlie Brown", "charlie@example.com", "5551112222", "789 Pine St"),
        ("Diana Prince", "diana@example.com", "5553334444", "101 Island Ave"),
        ("Evan Wright", "evan@example.com", "5555556666", "202 Tech Blvd"),
    ]
    
    customers = []
    for name, email, phone, address in customers_data:
        c, created = Customer.objects.get_or_create(name=name, email=email, defaults={'phone_number': phone, 'address': address})
        customers.append(c)
        if created:
            print(f"  -> Added Customer: {name}")

    # 2. Add more Products
    products_data = [
        ("Mechanical Keyboard", "RGB mechanical keyboard with blue switches", 89.99, 100),
        ("Gaming Monitor", "27-inch 144Hz 1080p Monitor", 249.99, 30),
        ("USB-C Hub", "7-in-1 Aluminum USB-C Hub", 35.00, 150),
        ("Noise Cancelling Headphones", "Over-ear wireless headphones", 199.99, 45),
        ("Webcam", "1080p HD Webcam with microphone", 49.99, 80),
    ]

    products = []
    for name, desc, price, stock in products_data:
        p, created = Product.objects.get_or_create(name=name, defaults={'description': desc, 'price': price, 'stock': stock})
        products.append(p)
        if created:
            print(f"  -> Added Product: {name}")

    # 3. Add Orders for these new customers
    for customer in customers:
        # Create an order
        order = Order.objects.create(customer=customer)
        print(f"  -> Created Order for {customer.name}")
        
        # Add 1 to 3 random products to their order
        num_items = random.randint(1, 3)
        chosen_products = random.sample(products, num_items)
        
        for prod in chosen_products:
            qty = random.randint(1, 2)
            OrderItem.objects.create(order=order, product=prod, quantity=qty, price=prod.price)
            print(f"      - Added {qty}x {prod.name} to order")
        
    print("\nFinished adding dummy data!")

if __name__ == '__main__':
    populate_more()
