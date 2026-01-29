from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    path('api/sales-data/', views.get_sales_data, name='sales_data'),
    path('api/product-performance/', views.get_product_performance, name='product_performance'),
    path('api/monthly-data/', views.get_monthly_data, name='monthly_data'),
]
