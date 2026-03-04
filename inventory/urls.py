from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('dashboard/', views.inventory_dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<uuid:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<uuid:product_id>/', views.delete_product, name='delete_product'),
    path('products/generate-barcode/<uuid:product_id>/', views.generate_barcode, name='generate_barcode'),
    path('sellers/', views.seller_list, name='seller_list'),
    path('sellers/add/', views.add_seller, name='add_seller'),
    path('sellers/toggle/<int:seller_id>/', views.toggle_seller, name='toggle_seller'),
    path('tax-config/', views.tax_config, name='tax_config'),
    path('loyalty-config/', views.loyalty_config, name='loyalty_config'),
    path('coupons/', views.coupon_list, name='coupon_list'),
    path('coupons/add/', views.add_coupon, name='add_coupon'),
    path('coupons/edit/<int:coupon_id>/', views.edit_coupon, name='edit_coupon'),
    path('coupons/toggle/<int:coupon_id>/', views.toggle_coupon, name='toggle_coupon'),
    path('backup/', views.trigger_backup, name='trigger_backup'),
    path('backup/manage/', views.backup_management, name='backup_management'),
    path('backup/restore/<str:backup_name>/', views.restore_backup, name='restore_backup'),
    path('backup/upload/', views.upload_backup, name='upload_backup'),
    path('backup/clear-all/', views.clear_all_data, name='clear_all_data'),
]
