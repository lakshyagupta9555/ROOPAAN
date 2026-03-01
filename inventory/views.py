from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import User, Product, TaxConfig, Seller, Coupon
from .forms import ProductForm, SellerForm, TaxConfigForm, CouponForm
from django.db.models import Q
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
from django.core.files import File
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import hashlib
import re


def generate_product_barcode(product):
    """Generate unique numeric barcode for scanner compatibility"""
    import random
    import hashlib
    
    # Create a seed from product attributes including brand
    brand = product.brand or "ROOPAAN'S"
    seed_string = f"{product.name}{brand}{product.size or ''}{product.colour or ''}"
    
    # Generate a hash and convert to numeric
    hash_object = hashlib.md5(seed_string.encode())
    hash_hex = hash_object.hexdigest()
    
    # Convert first 8 hex characters to numeric (base-10)
    numeric_hash = int(hash_hex[:8], 16)
    
    # Get last 8 digits to create barcode
    base_barcode = str(numeric_hash)[-8:]
    
    # Ensure it starts with a non-zero digit for EAN compatibility
    if base_barcode[0] == '0':
        base_barcode = '1' + base_barcode[1:]
    
    barcode = base_barcode
    
    # Ensure uniqueness by adding sequence number if needed
    counter = 0
    while Product.objects.filter(barcode=barcode).exists():
        counter += 1
        # Modify last 4 digits with counter
        barcode = base_barcode[:-4] + str(counter).zfill(4)
    
    return barcode


def is_inventory_manager(user):
    return user.is_authenticated and user.user_type == 'inventory'


def home(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'inventory':
            return redirect('inventory:dashboard')
        elif request.user.user_type == 'seller':
            # Check if seller has a profile
            try:
                request.user.seller_profile
                return redirect('seller:dashboard')
            except:
                from django.contrib.auth import logout
                logout(request)
                messages.error(request, 'Your seller account is not properly configured. Please contact an administrator.')
                return redirect('login')
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.user_type == user_type:
                login(request, user)
                messages.success(request, f'Welcome, {user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid user type for this account.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')


@login_required
@user_passes_test(is_inventory_manager)
def inventory_dashboard(request):
    products = Product.objects.all()[:10]
    sellers = Seller.objects.filter(is_active=True)
    low_stock_products = Product.objects.filter(quantity__lte=10)
    
    context = {
        'total_products': Product.objects.count(),
        'total_sellers': sellers.count(),
        'low_stock_count': low_stock_products.count(),
        'products': products,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'inventory/dashboard.html', context)


@login_required
@user_passes_test(is_inventory_manager)
def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(barcode__icontains=query)
        )
    
    context = {'products': products, 'query': query}
    return render(request, 'inventory/product_list.html', context)


@login_required
@user_passes_test(is_inventory_manager)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            
            # Auto-generate barcode if not provided
            if not product.barcode:
                product.barcode = generate_product_barcode(product)
            
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('inventory:product_list')
    else:
        form = ProductForm()
    
    return render(request, 'inventory/add_product.html', {'form': form})


@login_required
@user_passes_test(is_inventory_manager)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('inventory:product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'inventory/edit_product.html', {'form': form, 'product': product})


@login_required
@user_passes_test(is_inventory_manager)
def delete_product(request, product_id):
    from django.db.models.deletion import ProtectedError
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            product_name = product.name
            product.delete()
            messages.success(request, f'Product "{product_name}" deleted successfully!')
            return redirect('inventory:product_list')
        except ProtectedError:
            messages.error(request, f'Cannot delete "{product.name}" because it has associated sales records. Products with sales history cannot be deleted to maintain data integrity.')
            return redirect('inventory:product_list')
    
    return render(request, 'inventory/delete_product.html', {'product': product})


@login_required
@user_passes_test(is_inventory_manager)
def generate_barcode(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Clean the barcode value to ensure consistency - remove any whitespace
    barcode_value = str(product.barcode).strip().replace(' ', '').replace('\t', '').replace('\n', '')
    
    print(f"BARCODE GENERATION - Product: {product.name}, Barcode Value: [{barcode_value}] (len={len(barcode_value)}), ASCII: {[ord(c) for c in barcode_value]}")
    
    # Always use Code128 - it encodes the EXACT value without modification
    # EAN8/EAN13 recalculate checksums which causes scanner to read different values
    barcode_class = barcode.get_barcode_class('code128')
    print(f"Using Code128 for exact barcode encoding (no checksum modification)")
    
    # Configure the writer to show the exact barcode value
    writer_options = {
        'module_width': 0.3,
        'module_height': 15.0,
        'quiet_zone': 6.5,
        'font_size': 12,
        'text_distance': 5.0,
        'write_text': True,
    }
    
    ean = barcode_class(barcode_value, writer=ImageWriter())
    
    # Write barcode to buffer with options
    buffer = BytesIO()
    ean.write(buffer, options=writer_options)
    
    # Open the barcode image
    buffer.seek(0)
    barcode_image = Image.open(buffer)
    
    # Create a new image with extra space for store header and product info
    header_space = 50  # Space for "ROOPAAN STORE" at top
    footer_space = 140  # Space for product details below barcode
    new_height = barcode_image.height + header_space + footer_space
    new_image = Image.new('RGB', (barcode_image.width, new_height), 'white')
    
    # Add product details
    draw = ImageDraw.Draw(new_image)
    
    # Try to use a nice font, fallback to default if not available
    try:
        font_header = ImageFont.truetype("arialbd.ttf", 28)  # Bold for header
        font_large = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        try:
            font_header = ImageFont.truetype("arial.ttf", 28)
            font_large = ImageFont.truetype("arial.ttf", 20)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            font_header = ImageFont.load_default()
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Add "ROOPAAN STORE" header at the top
    store_text = "ROOPAAN STORE"
    bbox = draw.textbbox((0, 0), store_text, font=font_header)
    text_width = bbox[2] - bbox[0]
    text_x = (barcode_image.width - text_width) // 2
    draw.text((text_x, 10), store_text, fill='black', font=font_header)
    
    # Paste the barcode below the header
    new_image.paste(barcode_image, (0, header_space))
    
    # Starting Y position for text below barcode
    current_y = header_space + barcode_image.height + 10
    
    # Brand name
    brand_text = product.brand or "ROOPAAN'S"
    bbox = draw.textbbox((0, 0), brand_text, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_x = (barcode_image.width - text_width) // 2
    draw.text((text_x, current_y), brand_text, fill='black', font=font_large)
    current_y += 25
    
    # Product name
    name_text = product.name
    bbox = draw.textbbox((0, 0), name_text, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_x = (barcode_image.width - text_width) // 2
    draw.text((text_x, current_y), name_text, fill='black', font=font_large)
    current_y += 25
    
    # Size and Colour on same line if both exist
    size_colour_parts = []
    if product.size:
        size_colour_parts.append(f"Size: {product.size}")
    if product.colour:
        size_colour_parts.append(f"Colour: {product.colour}")
    
    if size_colour_parts:
        size_colour_text = " | ".join(size_colour_parts)
        bbox = draw.textbbox((0, 0), size_colour_text, font=font_small)
        text_width = bbox[2] - bbox[0]
        text_x = (barcode_image.width - text_width) // 2
        draw.text((text_x, current_y), size_colour_text, fill='black', font=font_small)
        current_y += 22
    
    # MRP text
    mrp_text = f"MRP: ₹{product.selling_price}"
    bbox = draw.textbbox((0, 0), mrp_text, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_x = (barcode_image.width - text_width) // 2
    draw.text((text_x, current_y), mrp_text, fill='black', font=font_large)
    
    # Save the combined image to buffer
    final_buffer = BytesIO()
    new_image.save(final_buffer, format='PNG')
    
    # Create a descriptive filename
    brand = product.brand or "ROOPAN'S"
    filename_parts = [brand, product.name]
    if product.size:
        filename_parts.append(product.size)
    if product.colour:
        filename_parts.append(product.colour)
    filename_parts.append(barcode_value)
    if product.colour:
        filename_parts.append(product.colour)
    filename_parts.append(barcode_value)
    
    # Clean filename for OS compatibility
    filename = "_".join(filename_parts).replace(" ", "_").replace("/", "-")
    filename = f"{filename}.png"
    
    response = HttpResponse(final_buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
@user_passes_test(is_inventory_manager)
def seller_list(request):
    sellers = Seller.objects.all()
    return render(request, 'inventory/seller_list.html', {'sellers': sellers})


@login_required
@user_passes_test(is_inventory_manager)
def add_seller(request):
    if request.method == 'POST':
        form = SellerForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            employee_id = form.cleaned_data['employee_id']
            
            try:
                # Create user
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    user_type='seller'
                )
                
                # Create seller profile
                seller = Seller.objects.create(
                    user=user,
                    employee_id=employee_id,
                    created_by=request.user
                )
                
                messages.success(request, f'Seller {username} added successfully!')
                return redirect('inventory:seller_list')
            except Exception as e:
                messages.error(request, f'Error creating seller: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SellerForm()
    
    return render(request, 'inventory/add_seller.html', {'form': form})


@login_required
@user_passes_test(is_inventory_manager)
def toggle_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    seller.is_active = not seller.is_active
    seller.save()
    
    status = "activated" if seller.is_active else "deactivated"
    messages.success(request, f'Seller {status} successfully!')
    
    return redirect('inventory:seller_list')


@login_required
@user_passes_test(is_inventory_manager)
def tax_config(request):
    config, created = TaxConfig.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        form = TaxConfigForm(request.POST, instance=config)
        if form.is_valid():
            tax_config = form.save(commit=False)
            tax_config.updated_by = request.user
            tax_config.save()
            messages.success(request, 'Tax configuration updated successfully!')
            return redirect('inventory:tax_config')
    else:
        form = TaxConfigForm(instance=config)
    
    return render(request, 'inventory/tax_config.html', {'form': form})


@login_required
@user_passes_test(is_inventory_manager)
def coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, 'inventory/coupon_list.html', {'coupons': coupons})


@login_required
@user_passes_test(is_inventory_manager)
def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.created_by = request.user
            coupon.save()
            messages.success(request, 'Coupon created successfully!')
            return redirect('inventory:coupon_list')
    else:
        form = CouponForm()
    
    return render(request, 'inventory/add_coupon.html', {'form': form})


@login_required
@user_passes_test(is_inventory_manager)
def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully!')
            return redirect('inventory:coupon_list')
    else:
        form = CouponForm(instance=coupon)
    
    return render(request, 'inventory/edit_coupon.html', {'form': form, 'coupon': coupon})


@login_required
@user_passes_test(is_inventory_manager)
def toggle_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.is_active = not coupon.is_active
    coupon.save()
    
    status = "activated" if coupon.is_active else "deactivated"
    messages.success(request, f'Coupon {status} successfully!')
    
    return redirect('inventory:coupon_list')


@login_required
@user_passes_test(is_inventory_manager)
def trigger_backup(request):
    from .utils import backup_to_google_drive
    
    try:
        result = backup_to_google_drive()
        messages.success(request, f'Backup completed successfully! {result}')
    except Exception as e:
        messages.error(request, f'Backup failed: {str(e)}')
    
    return redirect('inventory:dashboard')


@login_required
@user_passes_test(is_inventory_manager)
def backup_management(request):
    """List all available backups and handle restore"""
    from pathlib import Path
    from django.conf import settings
    
    backup_dir = settings.BASE_DIR / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    # Get list of backup files
    backups = []
    if backup_dir.exists():
        for backup_file in sorted(backup_dir.glob('*.sqlite3'), reverse=True):
            file_stats = backup_file.stat()
            backups.append({
                'name': backup_file.name,
                'path': str(backup_file),
                'size': file_stats.st_size / (1024 * 1024),  # Convert to MB
                'created': datetime.fromtimestamp(file_stats.st_mtime)
            })
    
    return render(request, 'inventory/backup_management.html', {'backups': backups})


@login_required
@user_passes_test(is_inventory_manager)
def restore_backup(request, backup_name):
    """Restore database from a backup file"""
    from pathlib import Path
    from django.conf import settings
    import shutil
    from django.db import connection
    
    if request.method == 'POST':
        try:
            backup_dir = settings.BASE_DIR / 'backups'
            backup_file = backup_dir / backup_name
            
            if not backup_file.exists():
                messages.error(request, 'Backup file not found!')
                return redirect('inventory:backup_management')
            
            # Verify it's a valid backup file
            if not backup_name.endswith('.sqlite3'):
                messages.error(request, 'Invalid backup file format!')
                return redirect('inventory:backup_management')
            
            # Create a backup of current database before restoring
            from .utils import backup_to_google_drive
            backup_to_google_drive()  # Create safety backup
            
            # Close all database connections
            connection.close()
            
            # Restore the backup
            db_path = settings.DATABASES['default']['NAME']
            shutil.copy2(backup_file, db_path)
            
            messages.success(request, f'Database restored successfully from {backup_name}!')
            messages.info(request, 'Please logout and login again for changes to take effect.')
            
        except Exception as e:
            messages.error(request, f'Restore failed: {str(e)}')
        
        return redirect('inventory:backup_management')
    
    return redirect('inventory:backup_management')


@login_required
@user_passes_test(is_inventory_manager)
def upload_backup(request):
    """Upload a backup database file"""
    from django.conf import settings
    import shutil
    
    if request.method == 'POST' and request.FILES.get('backup_file'):
        try:
            backup_file = request.FILES['backup_file']
            
            # Validate file extension
            if not backup_file.name.endswith('.sqlite3'):
                messages.error(request, 'Invalid file format! Please upload a .sqlite3 file.')
                return redirect('inventory:backup_management')
            
            # Validate file size (max 100MB)
            if backup_file.size > 100 * 1024 * 1024:
                messages.error(request, 'File too large! Maximum size is 100MB.')
                return redirect('inventory:backup_management')
            
            # Save to backups directory
            backup_dir = settings.BASE_DIR / 'backups'
            backup_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'uploaded_backup_{timestamp}.sqlite3'
            file_path = backup_dir / filename
            
            # Save the uploaded file
            with open(file_path, 'wb+') as destination:
                for chunk in backup_file.chunks():
                    destination.write(chunk)
            
            messages.success(request, f'Backup file uploaded successfully as {filename}!')
            messages.info(request, 'You can now restore from this backup.')
            
        except Exception as e:
            messages.error(request, f'Upload failed: {str(e)}')
        
        return redirect('inventory:backup_management')
    
    return redirect('inventory:backup_management')


@login_required
@user_passes_test(is_inventory_manager)
def clear_all_data(request):
    """Clear all sales, products, coupons data (keep users and sellers)"""
    from django.db import transaction
    from seller.models import Sale, SaleItem
    
    if request.method == 'POST':
        confirm = request.POST.get('confirm_text', '')
        
        if confirm != 'DELETE ALL DATA':
            messages.error(request, 'Confirmation text does not match. Data was not deleted.')
            return redirect('inventory:backup_management')
        
        try:
            # Create a safety backup first
            from .utils import backup_to_google_drive
            backup_to_google_drive()
            
            with transaction.atomic():
                # Delete all sales data
                sale_count = Sale.objects.count()
                sale_item_count = SaleItem.objects.count()
                Sale.objects.all().delete()
                
                # Delete all products
                product_count = Product.objects.count()
                Product.objects.all().delete()
                
                # Delete all coupons
                coupon_count = Coupon.objects.count()
                Coupon.objects.all().delete()
                
                messages.success(request, f'All data cleared successfully! Deleted: {product_count} products, {sale_count} sales, {sale_item_count} sale items, {coupon_count} coupons.')
                messages.info(request, 'A safety backup was created before deletion.')
            
        except Exception as e:
            messages.error(request, f'Failed to clear data: {str(e)}')
        
        return redirect('inventory:backup_management')
    
    return redirect('inventory:backup_management')

