# sydoc_project/sydoc_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('superadmin/', include('superadmin_panel.urls')), # If you decide to add custom superadmin views later
    path('center/', include('center_panel.urls')), # Add this line for the center panel
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'), # Redirect to login after logout
    # path('api/', include('api.urls')), # For future API endpoints
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)