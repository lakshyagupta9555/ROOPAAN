# Complete Installation Script for Inventory Management System
# This script will set up everything you need

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     INVENTORY MANAGEMENT SYSTEM - COMPLETE INSTALLER      " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Function to print status
function Print-Status {
    param($Message, $Type = "info")
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    switch ($Type) {
        "success" { Write-Host "[$timestamp] [OK] $Message" -ForegroundColor Green }
        "error"   { Write-Host "[$timestamp] [ERROR] $Message" -ForegroundColor Red }
        "info"    { Write-Host "[$timestamp] [INFO] $Message" -ForegroundColor Yellow }
        "step"    { Write-Host "`n[$timestamp] [STEP] $Message" -ForegroundColor Cyan }
    }
}

# Check Python installation
Print-Status "Checking Python installation..." "step"
try {
    $pythonVersion = python --version 2>&1
    Print-Status "Python found: $pythonVersion" "success"
} catch {
    Print-Status "Python not found! Please install Python 3.8+" "error"
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment
Print-Status "Setting up virtual environment..." "step"
if (Test-Path "venv") {
    Print-Status "Virtual environment already exists" "info"
} else {
    python -m venv venv
    if ($?) {
        Print-Status "Virtual environment created successfully" "success"
    } else {
        Print-Status "Failed to create virtual environment" "error"
        exit 1
    }
}

# Activate virtual environment
Print-Status "Activating virtual environment..." "step"
try {
    & .\venv\Scripts\Activate.ps1
    Print-Status "Virtual environment activated" "success"
} catch {
    Print-Status "Could not activate venv. Trying to fix permissions..." "info"
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    & .\venv\Scripts\Activate.ps1
    Print-Status "Virtual environment activated" "success"
}

# Upgrade pip
Print-Status "Upgrading pip..." "step"
python -m pip install --upgrade pip -q
Print-Status "Pip upgraded" "success"

# Install dependencies
Print-Status "Installing dependencies..." "step"
Print-Status "This may take a few minutes..." "info"
pip install -q -r requirements.txt
if ($?) {
    Print-Status "All dependencies installed successfully" "success"
} else {
    Print-Status "Some dependencies failed to install" "error"
}

# Create directories
Print-Status "Creating necessary directories..." "step"
$directories = @("static", "media", "backups", "media/products")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Print-Status "Created directory: $dir" "success"
    }
}

# Setup environment file
Print-Status "Setting up environment configuration..." "step"
if (Test-Path ".env") {
    Print-Status ".env file already exists" "info"
} else {
    Copy-Item ".env.example" ".env"
    $secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    (Get-Content ".env") -replace 'your-secret-key-here', $secretKey | Set-Content ".env"
    Print-Status "Environment file created with secure SECRET_KEY" "success"
}

# Run migrations
Print-Status "Setting up database..." "step"
python manage.py makemigrations 2>&1 | Out-Null
python manage.py migrate --noinput 2>&1 | Out-Null
Print-Status "Database created and migrated" "success"

# Collect static files
Print-Status "Collecting static files..." "step"
python manage.py collectstatic --noinput 2>&1 | Out-Null
Print-Status "Static files collected" "success"

# Create superuser
Print-Status "Creating admin account..." "step"
Write-Host ""
Write-Host "Please create an admin account for Inventory Manager:" -ForegroundColor Yellow
Write-Host "Username will be: admin" -ForegroundColor Cyan
$adminPassword = Read-Host "Enter admin password" -AsSecureString
$adminPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($adminPassword))

try {
    $env:DJANGO_SUPERUSER_PASSWORD = $adminPasswordPlain
    python -c @"
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
import django
django.setup()
from inventory.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', os.environ.get('DJANGO_SUPERUSER_PASSWORD'), user_type='inventory')
    print('created')
else:
    print('exists')
"@ | Out-Null
    Print-Status "Admin account ready" "success"
} catch {
    Print-Status "Admin account setup skipped" "info"
}

# Ask about sample data
Print-Status "Sample data setup..." "step"
Write-Host ""
$response = Read-Host "Do you want to create sample products and sellers for testing? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    Print-Status "Creating sample data..." "info"
    python create_sample_data.py
    Print-Status "Sample data created" "success"
} else {
    Print-Status "Skipping sample data creation" "info"
}

# Summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "              INSTALLATION COMPLETE!                        " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start the development server:" -ForegroundColor Yellow
Write-Host "   python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "2. Open your web browser and go to:" -ForegroundColor Yellow
Write-Host "   http://127.0.0.1:8000/" -ForegroundColor White
Write-Host ""
Write-Host "3. Login with:" -ForegroundColor Yellow
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: (what you just entered)" -ForegroundColor White
Write-Host "   Type: Inventory Manager" -ForegroundColor White
Write-Host ""

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host "SAMPLE DATA AVAILABLE:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Test Seller Account:" -ForegroundColor Yellow
    Write-Host "   - Username: seller1" -ForegroundColor White
    Write-Host "   - Password: seller123" -ForegroundColor White
    Write-Host ""
    Write-Host "   Test Barcodes (use in POS):" -ForegroundColor Yellow
    Write-Host "   - 1001 (Wireless Mouse)" -ForegroundColor White
    Write-Host "   - 1002 (USB Keyboard)" -ForegroundColor White
    Write-Host "   - 1005 (Phone Charger)" -ForegroundColor White
    Write-Host ""
    Write-Host "   Test Coupons:" -ForegroundColor Yellow
    Write-Host "   - WELCOME10 (10% off)" -ForegroundColor White
    Write-Host "   - FLAT50 (Rs.50 off)" -ForegroundColor White
    Write-Host "   - MEGA20 (20% off)" -ForegroundColor White
    Write-Host ""
}

Write-Host "DOCUMENTATION:" -ForegroundColor Cyan
Write-Host "   - START_HERE.md    - Overview and quick start" -ForegroundColor White
Write-Host "   - QUICKSTART.md    - Fast setup guide" -ForegroundColor White
Write-Host "   - README.md        - Complete documentation" -ForegroundColor White
Write-Host "   - FEATURES.md      - Full feature list" -ForegroundColor White
Write-Host ""

Write-Host "PRO TIPS:" -ForegroundColor Cyan
Write-Host "   - Use USB barcode scanner for fast product scanning" -ForegroundColor White
Write-Host "   - Create discount coupons for promotions" -ForegroundColor White
Write-Host "   - Check Analytics daily for insights" -ForegroundColor White
Write-Host "   - Backup database regularly" -ForegroundColor White
Write-Host ""

Write-Host "Happy selling! Your inventory system is ready to use!" -ForegroundColor Green
Write-Host ""

# Ask if user wants to start server now
$startNow = Read-Host "Start the server now? (Y/N)"
if ($startNow -eq "Y" -or $startNow -eq "y") {
    Write-Host ""
    Print-Status "Starting Django development server..." "step"
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    python manage.py runserver
} else {
    Write-Host ""
    Write-Host "To start the server later, run:" -ForegroundColor Yellow
    Write-Host "  python manage.py runserver" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
}
