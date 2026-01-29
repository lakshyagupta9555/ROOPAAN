# Inventory Management System - Quick Setup Script
# Run this script in PowerShell to set up the project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Inventory Management System Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/8] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "[2/8] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[3/8] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "[4/8] Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Set up environment file
Write-Host ""
Write-Host "[5/8] Setting up environment file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
} else {
    Copy-Item ".env.example" ".env"
    $secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    (Get-Content ".env") -replace 'your-secret-key-here', $secretKey | Set-Content ".env"
    Write-Host "✓ .env file created with new SECRET_KEY" -ForegroundColor Green
}

# Create static directory
Write-Host ""
Write-Host "[6/8] Creating static directory..." -ForegroundColor Yellow
if (-not (Test-Path "static")) {
    New-Item -ItemType Directory -Path "static" | Out-Null
}
Write-Host "✓ Static directory ready" -ForegroundColor Green

# Run migrations
Write-Host ""
Write-Host "[7/8] Running database migrations..." -ForegroundColor Yellow
python manage.py makemigrations --noinput
python manage.py migrate --noinput
Write-Host "✓ Database migrations completed" -ForegroundColor Green

# Create superuser instruction
Write-Host ""
Write-Host "[8/8] Creating superuser..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Now you need to create an inventory manager account." -ForegroundColor Cyan
Write-Host "Please enter the following details:" -ForegroundColor Cyan
Write-Host ""

$env:DJANGO_SUPERUSER_PASSWORD = Read-Host "Enter password for admin" -AsSecureString
$env:DJANGO_SUPERUSER_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($env:DJANGO_SUPERUSER_PASSWORD))

try {
    python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
import django
django.setup()
from inventory.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin'), user_type='inventory')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
    Write-Host "✓ Inventory manager account created" -ForegroundColor Green
} catch {
    Write-Host "Note: You may need to create superuser manually using:" -ForegroundColor Yellow
    Write-Host "python manage.py createsuperuser" -ForegroundColor Yellow
}

# Success message
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the server, run:" -ForegroundColor Cyan
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Then open your browser and go to:" -ForegroundColor Cyan
Write-Host "  http://127.0.0.1:8000/" -ForegroundColor White
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Cyan
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: (what you entered above)" -ForegroundColor White
Write-Host "  Login Type: Inventory Manager" -ForegroundColor White
Write-Host ""
Write-Host "Read README.md for more information!" -ForegroundColor Yellow
Write-Host ""
