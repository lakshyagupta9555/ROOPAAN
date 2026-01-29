from django.contrib import admin
from .models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['subtotal', 'tax_amount', 'total']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'seller', 'total_amount', 'payment_method', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['invoice_number', 'seller__user__username']
    inlines = [SaleItemInline]
    readonly_fields = ['invoice_number', 'subtotal', 'tax_amount', 'discount_amount', 'total_amount']

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'quantity', 'price', 'total']
    list_filter = ['sale__created_at']
    search_fields = ['product__name', 'sale__invoice_number']
