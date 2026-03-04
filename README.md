# Inventory Management System - Setup Instructions

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

## Step 1: Create Virtual Environment

Open PowerShell and navigate to the project directory:

```powershell
cd C:\Users\laksh\OneDrive\Desktop\inventory
python -m venv venv
```

## Step 2: Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

If you encounter an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

## Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

## Step 4: Set up Environment Variables

Copy the example environment file:
```powershell
copy .env.example .env
```

Generate a new SECRET_KEY:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Edit `.env` file and paste the generated secret key.

## Step 5: Run Migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

## Step 6: Create Superuser (Inventory Manager)

```powershell
python manage.py createsuperuser
```

When prompted:
- Username: admin
- Email: admin@example.com
- Password: (your choice)
- User type: Select 'inventory'

## Step 7: Create Static Files Directory

```powershell
mkdir static
python manage.py collectstatic --noinput
```

## Step 8: Run the Development Server

```powershell
python manage.py runserver
```

The application will be available at: http://127.0.0.1:8000/

## Default Login Credentials

**Inventory Manager:**
- Username: admin
- Password: (what you set in step 6)
- Login Type: Inventory Manager

## Creating a Seller Account

1. Log in as Inventory Manager
2. Navigate to "Sellers" menu
3. Click "Add Seller"
4. Fill in the details:
   - Username: seller1
   - Email: seller1@example.com
   - Password: (set a password)
   - Employee ID: EMP001

5. The seller can now login with:
   - Username: seller1
   - Password: (password you set)
   - Login Type: Seller

## Features

### Inventory Manager Interface:
- ✅ Manage products (add, edit, delete)
- ✅ Add sellers
- ✅ Configure CGST/SGST rates
- ✅ Create and manage coupons/discounts
- ✅ View analytics and reports
- ✅ Backup database
- ✅ Generate barcodes

### Seller Interface:
- ✅ Point of Sale (POS) system
- ✅ Barcode scanning support
- ✅ Add products to cart manually or by scanning
- ✅ Apply coupons/discounts
- ✅ Multiple payment methods (Cash, Card, UPI)
- ✅ Generate and print invoices
- ✅ Real-time inventory sync

## Barcode Scanning

To use barcode scanning:
1. Connect a USB barcode scanner to your computer
2. Go to the POS system
3. Focus on the "Scan or Enter Barcode" input field
4. Scan the barcode - it will automatically search and add to cart

## Google Drive Backup Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Download the credentials as `credentials.json`
6. Place it in the project root directory
7. Update `.env` file with the path to credentials

## Database Backup

Manual backup:
```powershell
python manage.py dumpdata > backup.json
```

Via web interface:
- Login as Inventory Manager
- Click "Backup Database" button on dashboard

## Troubleshooting

### Port already in use:
```powershell
python manage.py runserver 8080
```

### Static files not loading:
```powershell
python manage.py collectstatic --clear
```

### Database errors:
Delete db.sqlite3 and run migrations again:
```powershell
del db.sqlite3
python manage.py makemigrations
python manage.py migrate
```

## Additional Features to Explore

1. **Product Management**: Add products with images, costs, and barcodes
2. **Tax Configuration**: Set up custom CGST/SGST rates
3. **Coupon System**: Create percentage or fixed-amount discounts
4. **Analytics**: View profit/loss, revenue trends, top products
5. **Low Stock Alerts**: Automatic notifications for low inventory
6. **Invoice Generation**: Print or save invoices as PDF

## Support

For issues or questions, check:
- Django documentation: https://docs.djangoproject.com/
- Tailwind CSS: https://tailwindcss.com/docs
- Python Barcode: https://python-barcode.readthedocs.io/
