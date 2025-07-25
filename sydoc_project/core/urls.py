from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', login_required(views.profile), name='profile'),
    path('profile/edit/', login_required(views.edit_profile), name='edit_profile'),
    
    # Two-Factor Authentication
    path('login/verify/', views.TwoFactorVerifyView.as_view(), name='verify_2fa'),
    path('login/otp/resend/', views.resend_otp, name='otp_resend'),  # Keep for OTP resend functionality
    path('login/otp/debug/', views.debug_otp, name='otp_debug')  # Debug endpoint
]
