from django.contrib import admin
from .models import Sale, SaleItem, Customer

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['subtotal', 'tax_amount', 'total']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'seller', 'customer_name', 'customer_phone', 'total_amount', 'payment_method', 'loyalty_discount_applied', 'created_at']
    list_filter = ['payment_method', 'loyalty_discount_applied', 'created_at']
    search_fields = ['invoice_number', 'seller__user__username', 'customer_name', 'customer_phone']
    inlines = [SaleItemInline]
    readonly_fields = ['invoice_number', 'subtotal', 'tax_amount', 'discount_amount', 'total_amount']

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'quantity', 'price', 'total']
    list_filter = ['sale__created_at']
    search_fields = ['product__name', 'sale__invoice_number']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'total_visits', 'total_spent', 'first_visit', 'last_visit']
    list_filter = ['first_visit', 'last_visit']
    search_fields = ['name', 'phone']
    readonly_fields = ['first_visit', 'last_visit', 'total_visits', 'total_spent']
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'phone')
        }),
        ('Visit History', {
            'fields': ('total_visits', 'total_spent', 'first_visit', 'last_visit'),
            'classes': ('collapse',)
        }),
    )
