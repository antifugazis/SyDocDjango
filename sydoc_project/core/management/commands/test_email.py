from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send a test email to verify email configuration'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to send the test email to')

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write(self.style.SUCCESS(f'Sending test email to {email}...'))
        
        # Test simple email
        try:
            send_mail(
                'Test Email from SYDOC',
                'This is a test email from SYDOC. If you can read this, email is working!',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('Simple test email sent successfully!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error sending simple test email: {str(e)}'))
        
        # Test HTML email (like the OTP email)
        try:
            context = {
                'otp_code': '123456',
                'expiry_minutes': 3
            }
            
            subject = 'Test OTP Email from SYDOC'
            text_content = render_to_string('core/emails/otp_email.txt', context)
            html_content = render_to_string('core/emails/otp_email.html', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            
            self.stdout.write(self.style.SUCCESS('HTML test email (OTP style) sent successfully!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error sending HTML test email: {str(e)}'))
            
        self.stdout.write(self.style.SUCCESS('Test email process completed.'))
