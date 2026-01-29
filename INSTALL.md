# 🚀 INSTALLATION GUIDE

## Super Quick Install (Recommended)

Just run this one command in PowerShell:

```powershell
.\install.ps1
```

This automated script will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Set up database
- ✅ Create admin account
- ✅ Create sample data (optional)
- ✅ Start the server

---

## Manual Installation

If you prefer to install manually:

### 1. Create Virtual Environment
```powershell
python -m venv venv
```

### 2. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Set Up Environment
```powershell
copy .env.example .env
```

Edit `.env` and add a SECRET_KEY (generate with Python):
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Run Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Admin Account
```powershell
python manage.py createsuperuser
```

Enter:
- Username: `admin`
- Email: `admin@example.com`
- Password: (your choice)

When asked for user_type, it might not ask - that's OK.

Then run this to set user type:
```powershell
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings'); import django; django.setup(); from inventory.models import User; u = User.objects.get(username='admin'); u.user_type='inventory'; u.save(); print('Admin user type set to inventory')"
```

### 7. Create Static Files
```powershell
mkdir static
python manage.py collectstatic
```

### 8. (Optional) Create Sample Data
```powershell
python create_sample_data.py
```

### 9. Start Server
```powershell
python manage.py runserver
```

### 10. Open Browser
Go to: http://127.0.0.1:8000/

Login with:
- Username: `admin`
- Password: (what you set)
- Type: Inventory Manager

---

## What's Included

### Apps
- **inventory** - Product & seller management
- **seller** - POS system
- **analytics** - Reports & insights

### Features
- ✅ User authentication (Inventory Manager + Sellers)
- ✅ Product management with barcodes
- ✅ Point of Sale (POS) system
- ✅ Barcode scanning support
- ✅ Tax calculation (CGST/SGST)
- ✅ Coupon & discount system
- ✅ Multiple payment methods
- ✅ Invoice generation
- ✅ Analytics dashboard
- ✅ Database backup
- ✅ Dark theme UI

### Tech Stack
- Django 5.0
- SQLite database
- Tailwind CSS
- Python Barcode
- Google Drive API (optional)

---

## First Steps After Installation

### 1. Add Products
- Login as Inventory Manager
- Go to "Products" → "Add Product"
- Fill in product details
- Save

### 2. Create Sellers
- Go to "Sellers" → "Add Seller"
- Enter username, email, password, employee ID
- Save

### 3. Configure Taxes
- Go to "Tax Config"
- Set CGST and SGST rates
- Save

### 4. Create Coupons
- Go to "Coupons" → "Add Coupon"
- Set code, discount type, value, validity
- Save

### 5. Test POS
- Logout
- Login as seller
- Go to POS
- Search/scan products
- Add to cart
- Checkout

---

## Sample Data

If you created sample data during installation:

### Sample Seller
- Username: `seller1`
- Password: `seller123`

### Sample Products (Barcodes)
- 1001 - Wireless Mouse (₹599)
- 1002 - USB Keyboard (₹899)
- 1003 - HDMI Cable (₹299)
- 1004 - Laptop Stand (₹1299)
- 1005 - Phone Charger (₹799) *Low Stock*
- 1006 - Bluetooth Speaker (₹1999)
- 1007 - USB Flash Drive (₹399)
- 1008 - Webcam HD (₹2499)

### Sample Coupons
- **WELCOME10** - 10% off on ₹500+
- **FLAT50** - ₹50 off on ₹300+
- **MEGA20** - 20% off on ₹1000+ (max ₹200)

---

## Barcode Scanner Setup

1. Connect USB barcode scanner
2. No driver needed (works as keyboard)
3. Open POS system
4. Click in barcode field
5. Scan product barcode
6. Product auto-adds to cart

---

## Common Issues

### Virtual Environment Won't Activate
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port 8000 Already in Use
```powershell
python manage.py runserver 8080
```

### Static Files Not Loading
```powershell
python manage.py collectstatic --clear
```

### Reset Database
```powershell
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Forgot Admin Password
```powershell
python manage.py changepassword admin
```

---

## File Structure

```
inventory/
├── inventory_system/     # Django project
├── inventory/           # Inventory app
├── seller/              # Seller/POS app
├── analytics/           # Analytics app
├── templates/           # HTML templates
├── static/              # Static files
├── media/               # Uploads
├── venv/                # Virtual environment
├── db.sqlite3          # Database
├── manage.py           # Django CLI
├── requirements.txt    # Dependencies
└── install.ps1         # Auto installer
```

---

## Security Notes

- Change `SECRET_KEY` in `.env` for production
- Set `DEBUG=False` in production
- Use strong passwords
- Regular database backups
- Keep dependencies updated

---

## Backup & Restore

### Backup Database
Via Web:
- Login as Inventory Manager
- Click "Backup Database" button

Via Command:
```powershell
python manage.py dumpdata > backup.json
```

### Restore Database
```powershell
python manage.py loaddata backup.json
```

---

## Updating

### Update Dependencies
```powershell
pip install -r requirements.txt --upgrade
```

### Run Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

---

## Production Deployment

For production use:

1. Set `DEBUG=False` in `.env`
2. Use PostgreSQL instead of SQLite
3. Configure allowed hosts
4. Use gunicorn/uwsgi
5. Set up nginx reverse proxy
6. Enable HTTPS
7. Regular backups

---

## Support & Documentation

- **START_HERE.md** - Quick overview
- **README.md** - Full documentation  
- **QUICKSTART.md** - Fast setup
- **FEATURES.md** - Feature list

---

## Success!

If you see the login page at http://127.0.0.1:8000/ - you're all set! 🎉

Start selling! 🚀
