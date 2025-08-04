from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden
from functools import wraps


def get_user_group_names(user):
    """
    Get a list of group names that the user belongs to.
    
    Args:
        user: Django User object
        
    Returns:
        list: List of group names
    """
    return list(user.groups.values_list('name', flat=True))


def is_user_in_group(user, group_name):
    """
    Check if a user belongs to a specific group.
    
    Args:
        user: Django User object
        group_name: Name of the group to check
        
    Returns:
        bool: True if user is in the group, False otherwise
    """
    return user.groups.filter(name=group_name).exists()


def get_user_highest_privilege_group(user):
    """
    Get the highest privilege group for a user based on the hierarchy:
    Super Admin > Admin > Documentation Center > Member
    
    Args:
        user: Django User object
        
    Returns:
        str: Name of the highest privilege group, or None if user is in no groups
    """
    user_groups = get_user_group_names(user)
    
    # Check in order of privilege hierarchy
    if 'Super Admin' in user_groups:
        return 'Super Admin'
    elif 'Admin' in user_groups:
        return 'Admin'
    elif 'Documentation Center' in user_groups:
        return 'Documentation Center'
    elif 'Member' in user_groups:
        return 'Member'
    
    return None


def require_groups(user, group_names):
    """
    Check if user belongs to any of the specified groups.
    
    Args:
        user: Django User object
        group_names: List of group names
        
    Returns:
        bool: True if user is in any of the groups, False otherwise
    """
    if isinstance(group_names, str):
        group_names = [group_names]
    
    return user.groups.filter(name__in=group_names).exists()


def require_groups_decorator(group_names):
    """
    Decorator that restricts access to users who belong to at least one of the specified groups.
    Super Admin users are allowed to access all views.
    
    Args:
        group_names: List of group names or a single group name string
        
    Returns:
        Function decorator that checks if the user belongs to any of the specified groups
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect('login')
                
            # Allow Super Admin users to access all views
            if request.user.groups.filter(name='Super Admin').exists():
                return view_func(request, *args, **kwargs)
                
            if require_groups(request.user, group_names):
                return view_func(request, *args, **kwargs)
            else:
                from django.contrib import messages
                from django.shortcuts import redirect
                messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
                return redirect('login')
        return _wrapped_view
    return decorator
