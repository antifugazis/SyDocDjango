# sydoc_project/sydoc_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from core.views import TwoFactorLoginView

urlpatterns = [
    path('', include('core.urls')),  # Core app URLs (home, profile, etc.)
    path('admin/', admin.site.urls),
    path('superadmin/', include('superadmin_panel.urls')),  # Custom superadmin views
    path('center/', include('center_panel.urls')),  # Center panel functionality
    path('login/', TwoFactorLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),
    # path('api/', include('api.urls')),  # For future API endpoints
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# This ensures static files work in production with WhiteNoise
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)