from django.contrib import admin
from django.urls import path, include, re_path
from core.views import FrontendAppView
from django.conf import settings
from django.conf.urls.static import static

import os

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('inventory/', include('inventory.urls')),
    path('customer/', include('customer.urls')),
    path('sales/', include('sales.urls')),
    re_path(r'^.*$', FrontendAppView.as_view(), name='frontend'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)