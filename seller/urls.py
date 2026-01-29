from django.urls import path
from . import views

app_name = 'seller'

urlpatterns = [
    path('dashboard/', views.seller_dashboard, name='dashboard'),
    path('pos/', views.pos_system, name='pos'),
    path('api/search-product/', views.search_product, name='search_product'),
    path('api/validate-coupon/', views.validate_coupon, name='validate_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    path('invoice/<uuid:sale_id>/', views.view_invoice, name='view_invoice'),
    path('invoice/<uuid:sale_id>/print/', views.print_invoice, name='print_invoice'),
]
