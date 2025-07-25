# Standard library imports
import logging
import random
import string
from datetime import datetime, timedelta

# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives, send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import REDIRECT_FIELD_NAME


def mask_email(email):
    """Mask the email for display (e.g., j***@example.com)"""
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@')
    masked_username = username[0] + '*' * (len(username) - 1)
    return f"{masked_username}@{domain}"
from django.views import View
from django.contrib.auth.views import LoginView

# Local application imports
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile, OTP

# Set up logging
logger = logging.getLogger(__name__)

def send_otp_email(email, otp):
    """
    Send OTP to user's email with enhanced error handling and logging
    
    Args:
        email (str): Recipient's email address
        otp (OTP): OTP object containing the code and expiration
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        if not email or not otp or not hasattr(otp, 'otp') or not hasattr(otp, 'expires_at'):
            logger.error(f'Invalid OTP or email for sending: email={email}, otp={otp}')
            return False
            
        subject = _('Votre code de vérification SYDOC')
        context = {
            'otp_code': otp.otp,
            'expiry_minutes': 3
        }
        
        text_content = render_to_string('core/emails/otp_email.txt', context)
        html_content = render_to_string('core/emails/otp_email.html', context)
        
        # For development, just print to console
        if settings.DEBUG:
            logger.info(f'[DEV] OTP Email would be sent to {mask_email(email)} with code {otp.otp}')
            # Even in debug mode, try to send the actual email unless explicitly using console backend
            if settings.EMAIL_BACKEND.endswith('console.EmailBackend'):
                logger.info(f'Using console backend, not sending actual email')
                return True
            
        # Attempt to send the actual email
        try:
            email_message = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send(fail_silently=False)
            
            logger.info(f'OTP email sent successfully to {mask_email(email)}')
            return True
        except Exception as email_error:
            logger.error(f'SMTP Error sending OTP email: {str(email_error)}', exc_info=True)
            # If in debug mode, consider it sent anyway so testing can continue
            if settings.DEBUG:
                logger.warning('In DEBUG mode, continuing despite email error')
                return True
            return False
    except Exception as e:
        logger.error(f'Failed to send OTP email to {mask_email(email) if email else "unknown"}: {str(e)}', exc_info=True)
        return False

    def _clear_otp_session(self, request):
        """Clear OTP-related session data"""
        session_keys = ['otp_user_id', 'otp_email', 'otp_created_at']
        for key in session_keys:
            if key in request.session:
                del request.session[key]

class OTPVerifyView(View):
    """
    View for verifying OTP codes.
    """
    def post(self, request):
        otp_code = request.POST.get('otp', '').strip()
        user_id = request.session.get('otp_user_id')
        email = request.session.get('otp_email')
        
        logger.info(f"OTP verification attempt: code={otp_code}, user_id={user_id}, email={mask_email(email) if email else None}")
        logger.debug(f"Request POST data: {dict(request.POST)}")
        
        # Check session validity
        if not all([user_id, email]):
            logger.warning('OTP verification attempt with invalid session')
            return JsonResponse({
                'success': False,
                'error': 'Session expirée. Veuillez redémarrer le processus de connexion.',
                'debug_info': {'user_id': user_id is not None, 'email': email is not None}
            })

# OTPVerifyView has been removed as part of the migration to two-factor authentication only

def resend_otp(request):
    """Handle OTP resend requests with rate limiting and cooldown"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Méthode non autorisée.'
        }, status=405)
        
    user_id = request.session.get('otp_user_id')
    email = request.session.get('otp_email')
    
    if not all([user_id, email]):
        logger.warning('OTP resend attempt with invalid session')
        return JsonResponse({
            'success': False,
            'error': 'Session expirée. Veuillez redémarrer le processus de connexion.'
        }, status=400)
    
    # Check resend cooldown (60 seconds)
    resend_cooldown = 60  # seconds
    last_resend_time = request.session.get('otp_last_resend')
    
    if last_resend_time:
        last_resend = datetime.fromisoformat(last_resend_time)
        cooldown_remaining = int((last_resend + timedelta(seconds=resend_cooldown) - timezone.now()).total_seconds())
        
        if cooldown_remaining > 0:
            return JsonResponse({
                'success': False,
                'error': f'Veuillez patienter {cooldown_remaining} secondes avant de demander un nouveau code.'
            }, status=429)
    
    # Check max resend attempts
    max_resend_attempts = 3
    resend_count = request.session.get('otp_resend_count', 0)
    
    if resend_count >= max_resend_attempts:
        logger.warning(f'Max OTP resend attempts reached for user {user_id}')
        return JsonResponse({
            'success': False,
            'error': 'Nombre maximum de tentatives atteint. Veuillez réessayer plus tard.'
        }, status=429)
    
    try:
        user = User.objects.get(id=user_id, email=email, is_active=True)
        
        # Generate and send new OTP
        try:
            otp = OTP.create_otp_for_user(user)
            logger.info(f'Generated new OTP for user {user_id} (resend)')
        except Exception as e:
            logger.error(f'Error generating OTP for resend: {str(e)}', exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Erreur lors de la génération du code. Veuillez réessayer.'
            }, status=500)
        
        # Send the new OTP
        if not send_otp_email(user.email, otp):
            return JsonResponse({
                'success': False,
                'error': 'Erreur lors de l\'envoi du code. Veuillez réessayer.'
            }, status=500)
        
        # Update resend tracking
        request.session['otp_last_resend'] = timezone.now().isoformat()
        request.session['otp_resend_count'] = resend_count + 1
        request.session.modified = True
        
        logger.info(f'Resent OTP to {mask_email(user.email)} (attempt {resend_count + 1})')
        
        return JsonResponse({
            'success': True,
            'message': f'Nouveau code envoyé à {mask_email(user.email)}',
            'masked_email': mask_email(user.email),
            'cooldown': resend_cooldown
        })
        
    except User.DoesNotExist:
        logger.error(f'User not found during OTP resend: id={user_id}, email={email}')
        return JsonResponse({
            'success': False,
            'error': 'Erreur lors de la vérification. Veuillez réessayer.'
    }, status=405)

def debug_otp(request):
    """
    Debug view for OTP issues
    """
    if not settings.DEBUG:
        return HttpResponse("Debug view only available in DEBUG mode", status=403)
        
    context = {
        'session_data': {
            'otp_user_id': request.session.get('otp_user_id'),
            'otp_email': request.session.get('otp_email'),
            'otp_created_at': request.session.get('otp_created_at'),
            'otp_last_resend': request.session.get('otp_last_resend'),
            'otp_resend_count': request.session.get('otp_resend_count'),
        },
        'csrf_token': request.META.get('CSRF_COOKIE', None),
    }
    
    # Check if there's a valid user in session
    user_id = request.session.get('otp_user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            context['user_found'] = True
            context['user_email'] = user.email
            
            # Check for valid OTPs
            otps = OTP.objects.filter(user=user, is_used=False).order_by('-created_at')
            if otps.exists():
                context['active_otps'] = [{
                    'otp': otp.otp,
                    'created_at': otp.created_at,
                    'expires_at': otp.expires_at,
                    'is_valid': otp.is_valid(),
                } for otp in otps]
            
            # Check cache
            cache_key = f'otp_{user_id}'
            cached_otp = cache.get(cache_key)
            if cached_otp:
                context['cached_otp'] = cached_otp
        except User.DoesNotExist:
            context['user_found'] = False
    
    return JsonResponse(context, json_dumps_params={'indent': 2})

def home(request):
    """
    Home page view.
    """
    return render(request, 'core/home.html')

@login_required
def profile(request):
    """
    View for viewing user profile.
    """
    # Get or create the user's profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    context = {
        'profile': profile,
        'title': _('Mon Profil')
    }

    return render(request, 'core/profile.html', context)

@login_required
def edit_profile(request):
    """
    View for editing user profile.
    """
    # Get or create the user's profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, _('Votre profil a été mis à jour avec succès!'))
            return redirect('core:profile')
        else:
            messages.error(request, _('Veuillez corriger les erreurs ci-dessous.'))
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'title': _('Modifier mon profil')
    }

    return render(request, 'core/profile_edit.html', context)


class TwoFactorLoginView(LoginView):
    """
    Custom login view that redirects to 2FA verification after successful username/password authentication
    """
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        """Security check complete. Log the user in and send OTP for 2FA."""
        # Get the user from the form
        user = form.get_user()
        
        # Store user info in session for the 2FA step
        self.request.session['2fa_user_id'] = user.id
        
        # Generate and send OTP
        otp_obj = OTP.create_otp_for_user(user)
        if not send_otp_email(user.email, otp_obj):
            messages.error(self.request, _('Erreur lors de l\'envoi du code de vérification. Veuillez réessayer.'))
            return self.form_invalid(form)
        
        # Store OTP info in session
        self.request.session['otp_created_at'] = timezone.now().isoformat()
        self.request.session['otp_email'] = user.email
        self.request.session.modified = True
        
        # Redirect to 2FA verification page
        logger.info(f'User {user.username} authenticated with password, redirecting to 2FA verification')
        return redirect('core:verify_2fa')


class TwoFactorVerifyView(View):
    """
    View for verifying 2FA codes after successful password authentication
    """
    
    def get(self, request):
        # Check if user has already authenticated with password
        user_id = request.session.get('2fa_user_id')
        if not user_id:
            messages.error(request, _('Veuillez vous connecter avec votre nom d\'utilisateur et mot de passe d\'abord.'))
            return redirect('login')
        
        try:
            user = User.objects.get(id=user_id)
            masked_email = mask_email(user.email)
            
            context = {
                'masked_email': masked_email,
                'title': _('Vérification en deux étapes')
            }
            return render(request, 'core/two_factor_verify.html', context)
        except User.DoesNotExist:
            # Clear session and redirect to login
            self._clear_2fa_session(request)
            messages.error(request, _('Session expirée. Veuillez vous reconnecter.'))
            return redirect('login')
    
    def post(self, request):
        # Get the OTP code from the form
        otp_code = request.POST.get('otp')
        user_id = request.session.get('2fa_user_id')
        
        if not user_id or not otp_code:
            messages.error(request, _('Informations de vérification incomplètes.'))
            return redirect('login')
        
        try:
            user = User.objects.get(id=user_id)
            
            # Validate OTP
            is_valid, error_message = OTP.validate_otp(user, otp_code)
            
            if is_valid:
                # Clear 2FA session data
                self._clear_2fa_session(request)
                
                # Log the user in
                login(request, user)
                
                # Redirect to the appropriate page
                redirect_to = request.session.get(REDIRECT_FIELD_NAME, settings.LOGIN_REDIRECT_URL)
                logger.info(f'User {user.username} successfully verified 2FA, redirecting to {redirect_to}')
                return redirect(redirect_to)
            else:
                messages.error(request, _(error_message))
                return self.get(request)
                
        except User.DoesNotExist:
            self._clear_2fa_session(request)
            messages.error(request, _('Session expirée. Veuillez vous reconnecter.'))
            return redirect('login')
    
    def _clear_2fa_session(self, request):
        """Clear 2FA-related session data"""
        for key in ['2fa_user_id', 'otp_email', 'otp_created_at']:
            if key in request.session:
                del request.session[key]
        request.session.modified = True
