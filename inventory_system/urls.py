"""
URL configuration for inventory_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from inventory import views as inventory_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inventory_views.login_view, name='login'),
    path('home/', inventory_views.home, name='home'),
    path('logout/', inventory_views.logout_view, name='logout'),
    path('inventory/', include('inventory.urls')),
    path('seller/', include('seller.urls')),
    path('analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
