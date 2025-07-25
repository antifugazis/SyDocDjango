from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', login_required(views.profile), name='profile'),
    path('profile/edit/', login_required(views.edit_profile), name='edit_profile'),
    
    # OTP Authentication
    path('login/otp/', views.OTPLoginView.as_view(), name='otp_login'),
    path('login/otp/send/', views.OTPLoginView.as_view(), name='otp_send'),  # Handles POST requests for sending OTP
    path('login/otp/verify/', views.OTPVerifyView.as_view(), name='otp_verify'),
    path('login/otp/resend/', views.resend_otp, name='otp_resend'),
    path('login/otp/debug/', views.debug_otp, name='otp_debug'),  # Debug endpoint
]
