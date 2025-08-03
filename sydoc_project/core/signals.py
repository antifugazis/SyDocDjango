from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from .models import Loan, Book, Member, Notification, DocumentationCenter
from center_panel.models import Complaint

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
