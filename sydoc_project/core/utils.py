from django.contrib.auth.models import Group


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
