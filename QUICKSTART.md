# Quick Start Guide

## Fastest Way to Get Started

1. Open PowerShell in this directory
2. Run the setup script:
   ```powershell
   .\setup.ps1
   ```
3. Start the server:
   ```powershell
   python manage.py runserver
   ```
4. Open browser: http://127.0.0.1:8000/

## First Time Login

**Inventory Manager:**
- Username: `admin`
- Password: (what you set during setup)
- Login Type: Select "Inventory Manager"

## Quick Actions

### 1. Add Your First Product
1. Login as Inventory Manager
2. Click "Products" → "Add Product"
3. Fill in:
   - Name: Test Product
   - Barcode: 123456789
   - Quantity: 100
   - Selling Price: 100
   - Cost Price: 50

### 2. Create a Seller Account
1. Click "Sellers" → "Add Seller"
2. Fill in:
   - Username: seller1
   - Email: seller1@example.com
   - Password: seller123
   - Employee ID: EMP001

### 3. Set Tax Rates
1. Click "Tax Config"
2. Set CGST: 9%
3. Set SGST: 9%

### 4. Create a Discount Coupon
1. Click "Coupons" → "Add Coupon"
2. Fill in:
   - Code: SAVE10
   - Type: Percentage
   - Value: 10
   - Valid From/Until: Set dates

### 5. Test the POS System
1. Logout and login as seller1
2. Click "Open POS System"
3. Enter barcode or search product
4. Add to cart
5. Select payment method
6. Complete sale

## Features Included

✅ **Inventory Management**
- Add/Edit/Delete products
- Track stock levels
- Generate barcodes
- Product images

✅ **User Management**
- Inventory Manager role
- Seller role
- Secure authentication

✅ **Point of Sale (POS)**
- Barcode scanning
- Manual product search
- Shopping cart
- Real-time inventory sync

✅ **Tax Configuration**
- CGST/SGST rates
- Automatic calculation
- Shown on invoices

✅ **Coupons & Discounts**
- Percentage discounts
- Fixed amount discounts
- Minimum purchase amount
- Usage limits
- Validity periods

✅ **Payment Methods**
- Cash
- Card
- UPI

✅ **Invoice System**
- Auto-generated invoice numbers
- Print invoices
- Save as PDF (via print)

✅ **Analytics Dashboard**
- Revenue tracking
- Sales statistics
- Top products
- Profit analysis
- Low stock alerts

✅ **Database Backup**
- Manual backup
- Google Drive integration (optional)

✅ **Dark Theme**
- Modern UI with Tailwind CSS
- Fully responsive

## Barcode Scanner Setup

1. Connect USB barcode scanner
2. Open POS system
3. Click in barcode input field
4. Scan any product barcode
5. Product auto-adds to cart

## Keyboard Shortcuts (POS)

- **Enter** after typing barcode → Search product
- **Tab** → Navigate between fields

## Troubleshooting

**Can't activate venv?**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Port 8000 busy?**
```powershell
python manage.py runserver 8080
```

**Forgot admin password?**
```powershell
python manage.py changepassword admin
```

## Next Steps

1. ✅ Add real products with images
2. ✅ Create seller accounts
3. ✅ Configure tax rates
4. ✅ Set up discount coupons
5. ✅ Test complete sale flow
6. ✅ Review analytics
7. ✅ Set up Google Drive backup (optional)

## Support

Check [README.md](README.md) for detailed documentation.

---

**Built with:** Django 5.0 | Tailwind CSS | SQLite | Python Barcode
