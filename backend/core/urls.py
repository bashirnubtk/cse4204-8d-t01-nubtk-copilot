from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django default administrative panel gateway
    path('superadmin/', admin.site.urls),
    
    # Central routing map pointing exactly to the portal_web sub-app location
    path('', include('apps.portal_web.urls')),
]

# Development server static and media files route handlers
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)