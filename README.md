# Inventory Management System

A comprehensive Django-based inventory management system with POS (Point of Sale) functionality, analytics, and multi-user support.

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

## Tech Stack

- Django 5.0
- SQLite (development) / PostgreSQL (production)
- Bootstrap for UI
- ReportLab for PDF generation
- Python Barcode & QR Code libraries

---

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Create Virtual Environment

```powershell
cd C:\Users\laksh\OneDrive\Desktop\inventory
python -m venv venv
```

### Step 2: Activate Virtual Environment

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
```

If you encounter an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set up Environment Variables

```bash
# Copy example file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Generate a SECRET_KEY:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Edit `.env` file with your settings.

### Step 5: Run Migrations

```bash
python manage.py migrate
```

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

When prompted, select 'inventory' as user type.

### Step 7: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 8: Run Development Server

```bash
python manage.py runserver
```

Access at: http://127.0.0.1:8000/

---

## Deployment on Render

### Prerequisites
- A GitHub account with your project pushed to a repository
- A Render account (sign up at https://render.com)

### Deployment Steps

#### 1. Push Code to GitHub

```bash
git init
git add .
git commit -m "Initial commit for Render deployment"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

#### 2. Create PostgreSQL Database on Render

1. Go to https://dashboard.render.com
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: inventory-db
   - **Database**: inventory_db
   - **User**: inventory_user
   - **Region**: Choose closest to you
4. Click "Create Database"
5. Copy the **Internal Database URL** (found in database info)

#### 3. Create Web Service on Render

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: inventory-system (or your choice)
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn inventory_system.wsgi:application`
   - **Instance Type**: Free or Starter

#### 4. Set Environment Variables

In the web service "Environment" tab, add:

```
SECRET_KEY=<generate-secure-random-key>
DEBUG=False
ALLOWED_HOSTS=<your-app-name>.onrender.com
CSRF_TRUSTED_ORIGINS=https://<your-app-name>.onrender.com
DATABASE_URL=<paste-internal-database-url-from-step-2>
PYTHON_VERSION=3.11.0
```

**Important**: 
- Replace `<your-app-name>` with your actual Render app name
- Use the Internal Database URL for DATABASE_URL
- Generate a strong SECRET_KEY

#### 5. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy
3. Monitor the logs for any errors
4. Wait for "Build successful" message

#### 6. Create Superuser in Production

1. In Render dashboard, go to your web service
2. Click "Shell" tab (or use "Connect" → "SSH")
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow prompts to create admin user

#### 7. Access Your App

Your app will be live at: `https://<your-app-name>.onrender.com`

### Alternative: Deploy with render.yaml

For infrastructure-as-code deployment:

1. Ensure `render.yaml` is in your repository root
2. In Render, click "New +" → "Blueprint"
3. Connect your repository
4. Render will auto-create web service and database based on render.yaml

---

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| SECRET_KEY | Django secret key | Yes | - |
| DEBUG | Debug mode | No | True |
| ALLOWED_HOSTS | Comma-separated allowed hosts | Yes | localhost,127.0.0.1 |
| CSRF_TRUSTED_ORIGINS | Comma-separated trusted origins | No | - |
| DATABASE_URL | PostgreSQL connection string | No | Uses SQLite |
| DATABASE_NAME | SQLite database name | No | db.sqlite3 |
| GOOGLE_DRIVE_ENABLED | Enable Google Drive backups | No | False |
| UPI_MERCHANT_ID | UPI merchant ID | No | merchant@upi |
| UPI_MERCHANT_NAME | UPI merchant name | No | Inventory Store |

---

## User Types

- **Inventory Manager**: Full access to inventory, products, sellers, analytics
- **Seller**: Access to POS system and their sales history

### Creating a Seller Account

1. Log in as Inventory Manager
2. Navigate to "Sellers" menu
3. Click "Add Seller"
4. Fill in details (username, email, password, employee ID)
5. Seller can then login via POS interface

---

## Admin Panel

All models are registered in Django admin:
- User Management
- Product Management
- Tax Configuration
- Seller Management
- Coupon Management
- Sales & Sale Items

Access at: `/admin`

---

## Additional Features

### Barcode Scanning
1. Connect USB barcode scanner
2. Open POS system
3. Focus on barcode input field
4. Scan product barcode - auto-adds to cart

### Database Backup
- **Manual**: `python manage.py dumpdata > backup.json`
- **Via UI**: Click "Backup Database" in inventory dashboard

### Google Drive Backup (Optional)
1. Create project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Drive API
3. Create OAuth 2.0 credentials
4. Download as `credentials.json`
5. Place in project root
6. Update `.env` with settings

---

## Troubleshooting

### Port already in use
```bash
python manage.py runserver 8080
```

### Static files not loading
```bash
python manage.py collectstatic --clear
```

### Database errors
```bash
# Delete and recreate database
rm db.sqlite3  # Linux/Mac
del db.sqlite3  # Windows
python manage.py migrate
```

### Render deployment issues
- Check build logs for errors
- Verify all environment variables are set
- Ensure DATABASE_URL uses Internal Database URL
- Check ALLOWED_HOSTS includes your Render domain

---

## Project Structure

```
inventory/              # Main inventory app
seller/                 # POS and sales app
analytics/              # Analytics and reporting
templates/              # HTML templates
static/                 # Static files
staticfiles/            # Collected static (production)
media/                  # User uploads
inventory_system/       # Django project settings
```

---

## Support & Documentation

- Django: https://docs.djangoproject.com/
- Render: https://render.com/docs
- Python Barcode: https://python-barcode.readthedocs.io/

---

## License

[Add your license here]


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
