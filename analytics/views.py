from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
from seller.models import Sale, SaleItem
from inventory.models import Product
from decimal import Decimal
import calendar


def is_inventory_manager(user):
    return user.is_authenticated and user.user_type == 'inventory'


@login_required
@user_passes_test(is_inventory_manager)
def analytics_dashboard(request):
    # Get date range
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Calculate metrics
    sales = Sale.objects.filter(created_at__date__gte=last_30_days)
    
    total_revenue = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_sales = sales.count()
    
    # Calculate profit
    total_profit = Decimal('0')
    for sale in sales:
        for item in sale.items.all():
            product = item.product
            profit_per_unit = product.selling_price - product.cost_price - product.import_duty
            total_profit += profit_per_unit * item.quantity
    
    # Top selling products
    top_products = SaleItem.objects.filter(
        sale__created_at__date__gte=last_30_days
    ).values(
        'product__name'
    ).annotate(
        total_qty=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price'))
    ).order_by('-total_qty')[:10]
    
    # Low stock alerts
    low_stock = Product.objects.filter(quantity__lte=10).order_by('quantity')
    
    # Monthly sales and revenue for the last 12 months
    twelve_months_ago = today - timedelta(days=365)
    monthly_data = Sale.objects.filter(
        created_at__date__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        revenue=Sum('total_amount'),
        sales_count=Count('id')
    ).order_by('month')
    
    # Format data for chart
    month_labels = []
    month_revenue = []
    month_sales = []
    
    for data in monthly_data:
        month_name = data['month'].strftime('%b %Y')
        month_labels.append(month_name)
        month_revenue.append(float(data['revenue'] or 0))
        month_sales.append(data['sales_count'])
    
    context = {
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'total_profit': total_profit,
        'top_products': top_products,
        'low_stock': low_stock,
        'month_labels': month_labels,
        'month_revenue': month_revenue,
        'month_sales': month_sales,
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
@user_passes_test(is_inventory_manager)
def get_sales_data(request):
    days = int(request.GET.get('days', 30))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    sales_by_date = Sale.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).extra(
        select={'date': 'DATE(created_at)'}
    ).values('date').annotate(
        revenue=Sum('total_amount'),
        count=Count('id')
    ).order_by('date')
    
    data = {
        'labels': [item['date'].strftime('%Y-%m-%d') for item in sales_by_date],
        'revenue': [float(item['revenue']) for item in sales_by_date],
        'count': [item['count'] for item in sales_by_date],
    }
    
    return JsonResponse(data)


@login_required
@user_passes_test(is_inventory_manager)
def get_product_performance(request):
    days = int(request.GET.get('days', 30))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    product_performance = SaleItem.objects.filter(
        sale__created_at__date__gte=start_date,
        sale__created_at__date__lte=end_date
    ).values(
        'product__name'
    ).annotate(
        total_qty=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price'))
    ).order_by('-total_revenue')[:10]
    
    data = {
        'labels': [item['product__name'] for item in product_performance],
        'quantities': [item['total_qty'] for item in product_performance],
        'revenue': [float(item['total_revenue']) for item in product_performance],
    }
    
    return JsonResponse(data)


@login_required
@user_passes_test(is_inventory_manager)
def get_monthly_data(request):
    """API endpoint for monthly sales and revenue data"""
    months = int(request.GET.get('months', 12))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=months * 30)
    
    monthly_data = Sale.objects.filter(
        created_at__date__gte=start_date
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        revenue=Sum('total_amount'),
        sales_count=Count('id')
    ).order_by('month')
    
    data = {
        'labels': [item['month'].strftime('%b %Y') for item in monthly_data],
        'revenue': [float(item['revenue'] or 0) for item in monthly_data],
        'sales': [item['sales_count'] for item in monthly_data],
    }
    
    return JsonResponse(data)
