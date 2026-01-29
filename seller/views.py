from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from inventory.models import Product, TaxConfig, Coupon
from .models import Sale, SaleItem, Seller
from decimal import Decimal
import json
import qrcode
from io import BytesIO
import base64
from django.conf import settings


def is_seller(user):
    return user.is_authenticated and user.user_type == 'seller'


def generate_upi_qr(amount):
    """Generate UPI QR code for payment"""
    # Get UPI details from settings
    upi_id = settings.UPI_MERCHANT_ID
    merchant_name = settings.UPI_MERCHANT_NAME
    
    # UPI URI format
    upi_string = f"upi://pay?pa={upi_id}&pn={merchant_name}&am={amount}&cu=INR"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_string)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


@login_required
@user_passes_test(is_seller)
def seller_dashboard(request):
    try:
        seller = request.user.seller_profile
    except Seller.DoesNotExist:
        from django.contrib.auth import logout
        logout(request)
        messages.error(request, 'You do not have a seller profile. Please contact the administrator.')
        return redirect('login')
    
    recent_sales = Sale.objects.filter(seller=seller)[:10]
    
    # Calculate today's stats
    from django.db.models import Sum, Count
    today = timezone.now().date()
    today_sales = Sale.objects.filter(seller=seller, created_at__date=today)
    
    today_revenue = today_sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    today_count = today_sales.count()
    
    context = {
        'recent_sales': recent_sales,
        'today_revenue': today_revenue,
        'today_count': today_count,
    }
    return render(request, 'seller/dashboard.html', context)


@login_required
@user_passes_test(is_seller)
def pos_system(request):
    products = Product.objects.filter(quantity__gt=0)
    tax_config, _ = TaxConfig.objects.get_or_create(id=1)
    
    context = {
        'products': products,
        'tax_config': tax_config,
    }
    return render(request, 'seller/pos.html', context)


@login_required
@user_passes_test(is_seller)
def search_product(request):
    query = request.GET.get('q', '')
    
    if not query:
        return JsonResponse({'products': []})
    
    products = Product.objects.filter(barcode=query).first()
    
    if products:
        data = {
            'id': str(products.id),
            'name': products.name,
            'barcode': products.barcode,
            'price': float(products.selling_price),
            'quantity': products.quantity,
        }
        return JsonResponse({'product': data})
    
    # If not found by barcode, search by name
    products_list = Product.objects.filter(name__icontains=query, quantity__gt=0)[:10]
    
    data = [{
        'id': str(p.id),
        'name': p.name,
        'barcode': p.barcode,
        'price': float(p.selling_price),
        'quantity': p.quantity,
    } for p in products_list]
    
    return JsonResponse({'products': data})


@login_required
@user_passes_test(is_seller)
def validate_coupon(request):
    code = request.GET.get('code', '')
    subtotal = Decimal(request.GET.get('subtotal', '0'))
    
    try:
        coupon = Coupon.objects.get(code=code)
        is_valid, message = coupon.is_valid()
        
        if not is_valid:
            return JsonResponse({'valid': False, 'message': message})
        
        if subtotal < coupon.min_purchase_amount:
            return JsonResponse({
                'valid': False, 
                'message': f'Minimum purchase amount of ₹{coupon.min_purchase_amount} required'
            })
        
        discount = coupon.calculate_discount(subtotal)
        
        return JsonResponse({
            'valid': True,
            'discount': float(discount),
            'message': f'Coupon applied successfully! Discount: ₹{discount}'
        })
        
    except Coupon.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Invalid coupon code'})


@login_required
@user_passes_test(is_seller)
def checkout(request):
    if request.method != 'POST':
        return redirect('seller:pos')
    
    try:
        data = json.loads(request.body)
        cart_items = data.get('items', [])
        payment_method = data.get('payment_method')
        coupon_code = data.get('coupon_code', '')
        upi_payment_confirmed = data.get('upi_payment_confirmed', False)
        
        if not cart_items or not payment_method:
            return JsonResponse({'success': False, 'message': 'Invalid data'})
        
        # For UPI payment, first generate QR code before processing
        if payment_method == 'upi' and not upi_payment_confirmed:
            # Calculate total for QR code
            seller = request.user.seller_profile
            tax_config, _ = TaxConfig.objects.get_or_create(id=1)
            
            subtotal = Decimal('0')
            for item in cart_items:
                product = Product.objects.get(id=item['product_id'])
                quantity = int(item['quantity'])
                subtotal += product.selling_price * quantity
            
            discount_amount = Decimal('0')
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    is_valid, message = coupon.is_valid()
                    if is_valid and subtotal >= coupon.min_purchase_amount:
                        discount_amount = coupon.calculate_discount(subtotal)
                except Coupon.DoesNotExist:
                    pass
            
            tax_rate = (tax_config.cgst_rate + tax_config.sgst_rate) / 100
            taxable_amount = subtotal - discount_amount
            tax_amount = taxable_amount * tax_rate
            total_amount = taxable_amount + tax_amount
            
            # Generate UPI QR code
            qr_data = generate_upi_qr(total_amount)
            
            return JsonResponse({
                'success': True,
                'requires_upi_payment': True,
                'qr_code': qr_data,
                'amount': float(total_amount)
            })
        
        seller = request.user.seller_profile
        tax_config, _ = TaxConfig.objects.get_or_create(id=1)
        
        with transaction.atomic():
            # Calculate totals
            subtotal = Decimal('0')
            items_data = []
            
            for item in cart_items:
                product = Product.objects.select_for_update().get(id=item['product_id'])
                quantity = int(item['quantity'])
                
                if product.quantity < quantity:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Insufficient stock for {product.name}'
                    })
                
                item_subtotal = product.selling_price * quantity
                subtotal += item_subtotal
                
                items_data.append({
                    'product': product,
                    'quantity': quantity,
                    'price': product.selling_price,
                    'name': product.name
                })
            
            # Apply coupon if provided
            discount_amount = Decimal('0')
            coupon = None
            
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    is_valid, message = coupon.is_valid()
                    
                    if is_valid and subtotal >= coupon.min_purchase_amount:
                        discount_amount = coupon.calculate_discount(subtotal)
                        coupon.times_used += 1
                        coupon.save()
                except Coupon.DoesNotExist:
                    pass
            
            # Calculate tax
            tax_rate = (tax_config.cgst_rate + tax_config.sgst_rate) / 100
            taxable_amount = subtotal - discount_amount
            tax_amount = taxable_amount * tax_rate
            total_amount = taxable_amount + tax_amount
            
            # Create sale
            sale = Sale.objects.create(
                invoice_number=Sale.generate_invoice_number(),
                seller=seller,
                payment_method=payment_method,
                subtotal=subtotal,
                tax_amount=tax_amount,
                discount_amount=discount_amount,
                coupon=coupon,
                total_amount=total_amount,
                cgst_rate=tax_config.cgst_rate,
                sgst_rate=tax_config.sgst_rate
            )
            
            # Create sale items and update inventory
            for item_data in items_data:
                SaleItem.objects.create(
                    sale=sale,
                    product=item_data['product'],
                    product_name=item_data['name'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                
                # Update product quantity
                item_data['product'].quantity -= item_data['quantity']
                item_data['product'].save()
            
            return JsonResponse({
                'success': True,
                'sale_id': str(sale.id),
                'invoice_number': sale.invoice_number,
                'message': 'Sale completed successfully!'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@user_passes_test(is_seller)
def view_invoice(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Check if seller owns this sale
    if sale.seller.user != request.user and request.user.user_type != 'inventory':
        messages.error(request, 'You do not have permission to view this invoice.')
        return redirect('seller:dashboard')
    
    context = {'sale': sale}
    return render(request, 'seller/invoice.html', context)


@login_required
@user_passes_test(is_seller)
def print_invoice(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Check if seller owns this sale
    if sale.seller.user != request.user and request.user.user_type != 'inventory':
        messages.error(request, 'You do not have permission to print this invoice.')
        return redirect('seller:dashboard')
    
    context = {'sale': sale}
    return render(request, 'seller/print_invoice.html', context)
