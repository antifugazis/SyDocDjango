from django import template
from django.db.models import Q
from core.models import Notification, ChatMessage

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_names):
    """
    Check if user belongs to any of the specified groups.
    Group names should be comma-separated.
    """
    if not user.is_authenticated:
        return False
    
    group_list = [name.strip() for name in group_names.split(',')]
    return user.groups.filter(name__in=group_list).exists()

@register.filter(name='has_permission')
def has_permission(user, permission):
    """Check if user has a specific permission."""
    if not user.is_authenticated:
        return False
    return user.has_perm(permission)

@register.simple_tag
def user_is_admin(user):
    """Check if user is Super Admin or Admin."""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=['Super Admin', 'Admin']).exists()

@register.simple_tag
def get_unread_notification_count(user):
    """
    Get the count of unread notifications for a user.
    For staff users, get their personal notifications.
    For superusers, also include center-wide notifications.
    """
    if not user.is_authenticated:
        return 0
    
    count = 0
    
    # For staff users, get their personal notifications
    if hasattr(user, 'staff_profile'):
        count += Notification.objects.filter(recipient_staff=user.staff_profile, is_read=False).count()
    
    # For superusers, also include center-wide notifications
    if user.is_superuser:
        from core.models import DocumentationCenter
        center = DocumentationCenter.objects.first()
        if center:
            count += Notification.objects.filter(recipient_center=center, is_read=False).count()
    
    return count

@register.simple_tag
def get_unread_chat_count(user):
    """
    Get the count of unread chat messages for a user.
    """
    if not user.is_authenticated:
        return 0
    
    # Count unread messages where the user is the recipient
    return ChatMessage.objects.filter(recipient=user, is_read=False).count()
