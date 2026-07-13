import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MiniEcom.settings')
django.setup()

from django.contrib.auth.models import User
from shop.models import Customer, Product, Order, OrderItem

def populate():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created with password 'admin123'")

    # Sample customers
    c1, _ = Customer.objects.get_or_create(name='Alice Smith', email='alice@example.com', phone_number='1234567890', address='123 Alice St')
    c2, _ = Customer.objects.get_or_create(name='Bob Jones', email='bob@example.com', phone_number='0987654321', address='456 Bob Ave')

    # Sample products
    p1, _ = Product.objects.get_or_create(name='Laptop', description='A high performance laptop', price=999.99, stock=50)
    p2, _ = Product.objects.get_or_create(name='Mouse', description='Wireless mouse', price=25.50, stock=200)

    # Sample orders
    o1, _ = Order.objects.get_or_create(customer=c1)
    OrderItem.objects.get_or_create(order=o1, product=p1, quantity=1, price=p1.price)
    OrderItem.objects.get_or_create(order=o1, product=p2, quantity=2, price=p2.price)

    o2, _ = Order.objects.get_or_create(customer=c2)
    OrderItem.objects.get_or_create(order=o2, product=p2, quantity=1, price=p2.price)

    print("Sample data populated successfully!")

if __name__ == '__main__':
    populate()
