"""
Create sample data for testing the inventory system
Run this after initial setup: python manage.py shell < create_sample_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from inventory.models import User, Product, TaxConfig, Seller, Coupon
from datetime import datetime, timedelta
from django.utils import timezone

print("Creating sample data...")

# Create or update tax config
tax_config, created = TaxConfig.objects.get_or_create(
    id=1,
    defaults={
        'cgst_rate': 9.00,
        'sgst_rate': 9.00
    }
)
print(f"✓ Tax Config: CGST {tax_config.cgst_rate}% | SGST {tax_config.sgst_rate}%")

# Get admin user
try:
    admin = User.objects.get(username='admin')
except User.DoesNotExist:
    print("⚠ Admin user not found. Please run 'python manage.py createsuperuser' first")
    admin = None

if admin:
    # Create sample products
    sample_products = [
        {
            'name': 'Wireless Mouse',
            'barcode': '1001',
            'quantity': 50,
            'selling_price': 599.00,
            'cost_price': 350.00,
            'import_duty': 25.00,
            'description': 'Ergonomic wireless mouse with USB receiver'
        },
        {
            'name': 'USB Keyboard',
            'barcode': '1002',
            'quantity': 30,
            'selling_price': 899.00,
            'cost_price': 500.00,
            'import_duty': 50.00,
            'description': 'Full-size USB keyboard with numeric keypad'
        },
        {
            'name': 'HDMI Cable 2m',
            'barcode': '1003',
            'quantity': 100,
            'selling_price': 299.00,
            'cost_price': 150.00,
            'import_duty': 10.00,
            'description': 'High-speed HDMI cable, 2 meters'
        },
        {
            'name': 'Laptop Stand',
            'barcode': '1004',
            'quantity': 20,
            'selling_price': 1299.00,
            'cost_price': 750.00,
            'import_duty': 75.00,
            'description': 'Adjustable aluminum laptop stand'
        },
        {
            'name': 'Phone Charger 20W',
            'barcode': '1005',
            'quantity': 8,  # Low stock
            'selling_price': 799.00,
            'cost_price': 450.00,
            'import_duty': 30.00,
            'description': 'Fast charging 20W USB-C charger'
        },
        {
            'name': 'Bluetooth Speaker',
            'barcode': '1006',
            'quantity': 15,
            'selling_price': 1999.00,
            'cost_price': 1200.00,
            'import_duty': 100.00,
            'description': 'Portable Bluetooth speaker with bass boost'
        },
        {
            'name': 'USB Flash Drive 32GB',
            'barcode': '1007',
            'quantity': 60,
            'selling_price': 399.00,
            'cost_price': 200.00,
            'import_duty': 15.00,
            'description': '32GB USB 3.0 flash drive'
        },
        {
            'name': 'Webcam HD',
            'barcode': '1008',
            'quantity': 12,
            'selling_price': 2499.00,
            'cost_price': 1500.00,
            'import_duty': 120.00,
            'description': '1080p HD webcam with built-in microphone'
        },
    ]

    for prod_data in sample_products:
        product, created = Product.objects.get_or_create(
            barcode=prod_data['barcode'],
            defaults={**prod_data, 'created_by': admin}
        )
        if created:
            print(f"✓ Created product: {product.name}")
        else:
            print(f"  Product already exists: {product.name}")

    # Create sample seller
    seller_username = 'seller1'
    if not User.objects.filter(username=seller_username).exists():
        seller_user = User.objects.create_user(
            username=seller_username,
            email='seller1@example.com',
            password='seller123',
            user_type='seller'
        )
        
        seller_profile = Seller.objects.create(
            user=seller_user,
            employee_id='EMP001',
            created_by=admin
        )
        print(f"✓ Created seller: {seller_username} (password: seller123)")
    else:
        print(f"  Seller already exists: {seller_username}")

    # Create sample coupons
    now = timezone.now()
    
    sample_coupons = [
        {
            'code': 'WELCOME10',
            'discount_type': 'percentage',
            'discount_value': 10.00,
            'min_purchase_amount': 500.00,
            'valid_from': now,
            'valid_until': now + timedelta(days=30),
            'is_active': True,
            'description': '10% off on purchases above ₹500'
        },
        {
            'code': 'FLAT50',
            'discount_type': 'fixed',
            'discount_value': 50.00,
            'min_purchase_amount': 300.00,
            'valid_from': now,
            'valid_until': now + timedelta(days=15),
            'is_active': True,
            'description': 'Flat ₹50 off on purchases above ₹300'
        },
        {
            'code': 'MEGA20',
            'discount_type': 'percentage',
            'discount_value': 20.00,
            'min_purchase_amount': 1000.00,
            'max_discount_amount': 200.00,
            'usage_limit': 50,
            'valid_from': now,
            'valid_until': now + timedelta(days=7),
            'is_active': True,
            'description': '20% off (max ₹200) on purchases above ₹1000'
        },
    ]

    for coupon_data in sample_coupons:
        desc = coupon_data.pop('description')
        coupon, created = Coupon.objects.get_or_create(
            code=coupon_data['code'],
            defaults={**coupon_data, 'created_by': admin}
        )
        if created:
            print(f"✓ Created coupon: {coupon.code} - {desc}")
        else:
            print(f"  Coupon already exists: {coupon.code}")

print("\n" + "="*60)
print("Sample data creation complete!")
print("="*60)
print("\n📦 Products created: 8 items")
print("👤 Seller account: seller1 (password: seller123)")
print("🎟️ Coupons created: 3 active coupons")
print("\n💡 Try these barcodes in POS:")
print("   - 1001 (Wireless Mouse)")
print("   - 1002 (USB Keyboard)")
print("   - 1005 (Phone Charger - Low Stock!)")
print("\n🎫 Try these coupons:")
print("   - WELCOME10 (10% off on ₹500+)")
print("   - FLAT50 (₹50 off on ₹300+)")
print("   - MEGA20 (20% off on ₹1000+)")
print("\n🚀 Ready to test! Run: python manage.py runserver")
