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


def mask_email(email):
    """Mask the email for display (e.g., j***@example.com)"""
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@')
    masked_username = username[0] + '*' * (len(username) - 1)
    return f"{masked_username}@{domain}"
from django.views import View

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

class OTPLoginView(View):
    """Handle OTP-based login requests with rate limiting and better error handling"""
    
    def get(self, request):
        # Clear any existing OTP session data
        for key in ['otp_user_id', 'otp_email', 'otp_created_at', 'otp_last_resend', 'otp_resend_count']:
            if key in request.session:
                del request.session[key]
        
        # Set a fresh CSRF token to ensure it's available
        request.META["CSRF_COOKIE_USED"] = True
                
        return render(request, 'core/otp_login.html')
    
    def post(self, request):
        email = request.POST.get('email', '').strip().lower()
        logger.info(f"OTP request for email: {mask_email(email)}")
        
        # Basic validation
        if not email or '@' not in email:
            logger.warning(f"Invalid email format: {mask_email(email)}")
            return JsonResponse({
                'success': False,
                'error': 'Veuillez fournir une adresse email valide.'
            }, status=400)
            
        # Check rate limiting
        cache_key = f'otp_attempts_{email}'
        attempts = cache.get(cache_key, 0)
        max_attempts = 5
        
        if attempts >= max_attempts:
            return JsonResponse({
                'success': False,
                'error': 'Trop de tentatives. Veuillez réessayer plus tard.'
            }, status=429)
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Generate and store OTP
            try:
                otp = OTP.create_otp_for_user(user)
                logger.info(f'Generated OTP for user {user.id}')
            except Exception as e:
                logger.error(f'Error generating OTP for user {user.id}: {str(e)}', exc_info=True)
                return JsonResponse({
                    'success': False,
                    'error': 'Erreur lors de la génération du code. Veuillez réessayer.'
                }, status=500)
            
            # Send OTP via email
            if not send_otp_email(user.email, otp):
                # Increment failed attempts
                cache.set(cache_key, attempts + 1, timeout=3600)  # 1 hour cooldown
                return JsonResponse({
                    'success': False,
                    'error': 'Erreur lors de l\'envoi du code. Veuillez réessayer.'
                }, status=500)
            
            # Store OTP info in session
            request.session['otp_user_id'] = user.id
            request.session['otp_email'] = user.email
            request.session['otp_created_at'] = timezone.now().isoformat()
            request.session['otp_last_resend'] = None
            request.session['otp_resend_count'] = 0
            
            # Ensure session is saved immediately
            request.session.save()
            logger.info(f"Session data saved with user_id={user.id}, session_key={request.session.session_key}")
            
            # Mask email for display
            masked_email = mask_email(email)
            
            return JsonResponse({
                'success': True,
                'message': f'Un code de vérification a été envoyé à {masked_email}',
                'masked_email': masked_email
            })
            
        except User.DoesNotExist:
            # Increment failed attempts for non-existent users too (security measure)
            cache.set(cache_key, attempts + 1, timeout=3600)
            logger.warning(f'Login attempt for non-existent email: {email}')
            return JsonResponse({
                'success': False,
                'error': 'Si un compte existe avec cette adresse email, un code de vérification vous a été envoyé.'
            }, status=400)
    
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
            }, status=400)
            
        # Validate OTP format
        if not otp_code or not otp_code.isdigit() or len(otp_code) != 6:
            return JsonResponse({
                'success': False,
                'error': 'Format de code invalide. Le code doit contenir 6 chiffres.'
            }, status=400)
            
        # Check rate limiting
        cache_key = f'otp_verify_attempts_{user_id}'
        attempts = cache.get(cache_key, 0)
        max_attempts = 5
        
        if attempts >= max_attempts:
            logger.warning(f'Too many OTP verification attempts for user {user_id}')
            return JsonResponse({
                'success': False,
                'error': 'Trop de tentatives échouées. Veuillez demander un nouveau code.'
            }, status=429)
            
        try:
            user = User.objects.get(id=user_id, email=email, is_active=True)
            
            # Validate OTP using the enhanced model method
            is_valid, error_message = OTP.validate_otp(user, otp_code)
            if not is_valid:
                # Increment failed attempts
                attempts += 1
                cache.set(cache_key, attempts, timeout=3600)  # 1 hour cooldown
                logger.warning(f'Invalid OTP attempt {attempts}/{max_attempts} for user {user_id}: {error_message}')
                
                # Calculate remaining attempts
                remaining_attempts = max(0, max_attempts - attempts)
                
                # If no more attempts left, clear the session for security
                if remaining_attempts <= 0:
                    request.session.flush()
                    return JsonResponse({
                        'success': False,
                        'error': 'Trop de tentatives échouées. Veuillez redémarrer le processus de connexion.',
                        'session_expired': True
                    }, status=429)
                    
                return JsonResponse({
                    'success': False,
                    'error': f'{error_message} Il vous reste {remaining_attempts} essai(s).',
                    'remaining_attempts': remaining_attempts
                }, status=400)
            
            # Clear any rate limiting on successful verification
            cache.delete(cache_key)
            
            # Log the user in
            login(request, user)
            logger.info(f'User {user_id} logged in successfully via OTP')
            
            # Clear all OTP-related session data
            session_keys = ['otp_user_id', 'otp_email', 'otp_created_at']
            for key in session_keys:
                if key in request.session:
                    del request.session[key]
            
            # Set session to expire after 2 weeks instead of browser close
            request.session.set_expiry(60 * 60 * 24 * 14)  # 14 days in seconds
            
            return JsonResponse({
                'success': True,
                'redirect_url': '/',  # Redirect to home page after login
                'message': 'Connexion réussie!'
            })
            
        except User.DoesNotExist:
            logger.error(f'User not found during OTP verification: id={user_id}, email={email}')
            return JsonResponse({
                'success': False,
                'error': 'Erreur lors de la vérification. Veuillez réessayer.'
            }, status=400)

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
