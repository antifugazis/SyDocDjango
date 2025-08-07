from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from .models import Loan, Book, Member, Notification, DocumentationCenter
from center_panel.models import Complaint
from django.core.mail import EmailMessage
from django.utils.crypto import get_random_string
from sydoc_project.settings import EMAIL_HOST_USER
import logging
import string

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DocumentationCenter)
def send_email_notification_on_documentation_create(sender, instance, created, **kwargs):
    if created:
        try:
            user_name = f"user_{instance.id}_{get_random_string(6, string.ascii_lowercase)}"
            password = get_random_string(12, string.ascii_letters + string.digits + "!@#$%")
            user, user_created = User.objects.get_or_create(
                email=instance.email,
                defaults={
                    'username': user_name,
                    'first_name': instance.name.split()[0] if instance.name else '',
                    'last_name': ' '.join(instance.name.split()[1:]) if len(instance.name.split()) > 1 else '',
                    'is_active': True,
                }
            )
            if user_created:
                user.set_password(password)
                user.save()
                logger.info(f"Created new user account for {instance.email}")
            else:
                user.set_password(password)
                user.save()
                logger.info(f"Updated password for existing user {instance.email}")
            download_link = getattr(settings, 'SYDOC_DOWNLOAD_LINK', 'https://sydoc.com/download')
            support_email = getattr(settings, 'SUPPORT_EMAIL', 'support@sydoc.com')
            company_website = getattr(settings, 'COMPANY_WEBSITE', 'https://sydoc.com')
            subject = 'Welcome to SyDoc - Your Account Details'
            plain_message = f"""
                            Dear {instance.name},

                            Welcome to SyDoc! We're excited to have you on board.

                            Your account has been successfully created with the following details:

                            Username: {user_name}
                            Password: {password}

                            You can download the SyDoc Software from: {download_link}

                            Getting Started:
                            1. Download the software using the link above
                            2. Install and launch the application
                            3. Log in using your credentials
                            4. Explore the Documentation Center features

                            For security reasons, we recommend changing your password after your first login.

                            If you need any assistance, please don't hesitate to contact our support team at {support_email}.

                            Thank you for choosing SyDoc!

                            Best regards,
                            The SyDoc Team

                            ---
                            This is an automated message. Please do not reply to this email.
                            Visit us at: {company_website}
                                        """.strip()
            
            email_msg = EmailMessage(
                subject=subject,
                body=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[instance.email],
            )
            email_msg.send()
            logger.info(f"Welcome email sent successfully to {instance.email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email to {instance.email}: {str(e)}")
            pass



@receiver(post_save, sender=Complaint)
def create_complaint_notification(sender, instance, created, **kwargs):
    """
    Create a notification when a new complaint is submitted
    """
    if created:
        # Get the first documentation center (main center)
        center = DocumentationCenter.objects.first()
        
        # Create notification for super admins
        Notification.objects.create(
            recipient_center=center,
            message=f"Nouvelle doléance reçue de {instance.full_name}",
            notification_type='alert'
        )

@receiver(post_save, sender=Loan)
def create_loan_notifications(sender, instance, created, **kwargs):
    """
    Create notifications for loan events:
    - New loan created
    - Loan returned
    - Loan approaching due date
    """
    # Get the documentation center (assuming there's only one or the first one)
    documentation_center = DocumentationCenter.objects.first()
    
    if created:
        # New loan notification
        Notification.objects.create(
            recipient_center=documentation_center,
            message=f"Nouveau prêt: {instance.book.title} prêté à {instance.member.full_name}",
            notification_type='info'
        )
        
        # Also create a notification for the member if they have a user account
        if hasattr(instance.member, 'user') and instance.member.user:
            # Check if member has a staff profile
            staff_profile = None
            if hasattr(instance.member, 'staff_profile'):
                staff_profile = instance.member.staff_profile
                
            if staff_profile:
                Notification.objects.create(
                    recipient_staff=staff_profile,
                    message=f"Vous avez emprunté: {instance.book.title}. À retourner avant le {instance.due_date.strftime('%d/%m/%Y')}",
                    notification_type='info'
                )
    else:
        # Check if the loan was just returned (status changed to 'returned')
        if instance.status == 'returned' and instance.return_date:
            Notification.objects.create(
                recipient_center=documentation_center,
                message=f"Livre retourné: {instance.book.title} par {instance.member.full_name}",
                notification_type='info'
            )

@receiver(pre_save, sender=Loan)
def check_overdue_loans(sender, instance, **kwargs):
    """
    Check if a loan is approaching its due date and create a notification
    """
    # Only run this for existing loans
    if instance.pk:
        # If the loan is not returned yet
        if not instance.return_date and instance.status not in ['returned', 'cancelled', 'rejected']:
            today = timezone.now().date()
            days_until_due = (instance.due_date - today).days
            
            # Check if member has a staff profile
            staff_profile = None
            if hasattr(instance.member, 'user') and instance.member.user and hasattr(instance.member, 'staff_profile'):
                staff_profile = instance.member.staff_profile
            
            # If due date is within 2 days
            if 0 <= days_until_due <= 2 and staff_profile:
                # Check if we already sent a notification for this (to avoid duplicates)
                recent_notifications = Notification.objects.filter(
                    recipient_staff=staff_profile,
                    message__contains=f"Rappel: {instance.book.title}",
                    created_at__gte=timezone.now() - timezone.timedelta(days=1)
                )
                
                if not recent_notifications.exists():
                    # Create a reminder notification
                    Notification.objects.create(
                        recipient_staff=staff_profile,
                        message=f"Rappel: {instance.book.title} doit être retourné avant le {instance.due_date.strftime('%d/%m/%Y')}",
                        notification_type='alert'
                    )
            
            # If the loan is overdue
            elif days_until_due < 0 and staff_profile:
                # Check if we already sent an overdue notification
                recent_notifications = Notification.objects.filter(
                    recipient_staff=staff_profile,
                    message__contains=f"RETARD: {instance.book.title}",
                    created_at__gte=timezone.now() - timezone.timedelta(days=3)
                )
                
                if not recent_notifications.exists():
                    # Create an overdue notification
                    Notification.objects.create(
                        recipient_staff=staff_profile,
                        message=f"RETARD: {instance.book.title} devait être retourné le {instance.due_date.strftime('%d/%m/%Y')}",
                        notification_type='alert'
                    )
                    
                    # Also notify the documentation center
                    documentation_center = DocumentationCenter.objects.first()
                    if documentation_center:
                        Notification.objects.create(
                            recipient_center=documentation_center,
                            message=f"RETARD: {instance.book.title} emprunté par {instance.member.full_name} devait être retourné le {instance.due_date.strftime('%d/%m/%Y')}",
                            notification_type='alert'
                        )

