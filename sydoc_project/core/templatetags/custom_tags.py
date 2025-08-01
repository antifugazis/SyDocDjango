from django import template

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
