from django.contrib import admin
from .models import User, Product, TaxConfig, Seller, Coupon, LoyaltyDiscountConfig

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'user_type', 'is_active']
    list_filter = ['user_type', 'is_active']
    search_fields = ['username', 'email']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'size', 'colour', 'barcode', 'quantity', 'selling_price', 'cost_price', 'is_in_stock']
    list_filter = ['created_at', 'brand', 'size', 'colour']
    search_fields = ['name', 'brand', 'barcode', 'size', 'colour']
    readonly_fields = ['barcode', 'created_at', 'updated_at', 'created_by']
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'brand', 'size', 'colour', 'barcode', 'description', 'image')
        }),
        ('Inventory', {
            'fields': ('quantity',)
        }),
        ('Pricing', {
            'fields': ('selling_price', 'cost_price', 'import_duty')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TaxConfig)
class TaxConfigAdmin(admin.ModelAdmin):
    list_display = ['cgst_rate', 'sgst_rate', 'updated_at']

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'employee_id']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'valid_from', 'valid_until', 'times_used']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code']
    readonly_fields = ['times_used', 'created_at']

@admin.register(LoyaltyDiscountConfig)
class LoyaltyDiscountConfigAdmin(admin.ModelAdmin):
    list_display = ['is_active', 'discount_type', 'discount_value', 'min_days_between_visits', 'max_days_between_visits', 'updated_at']
    list_filter = ['is_active', 'discount_type']
    fieldsets = (
        ('Discount Settings', {
            'fields': ('is_active', 'discount_type', 'discount_value', 'max_discount_amount')
        }),
        ('Time Period Settings', {
            'fields': ('min_days_between_visits', 'max_days_between_visits'),
            'description': 'Define the time window for loyalty discount eligibility'
        }),
        ('Requirements', {
            'fields': ('min_purchase_amount',)
        }),
        ('Metadata', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['updated_at']
