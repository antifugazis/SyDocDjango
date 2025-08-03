"""
Views for testing group-based permissions.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from core.utils import get_user_group_names, is_user_in_group, get_user_highest_privilege_group, require_groups


@login_required
def group_info(request):
    """
    Display the user's group information.
    """
    user_groups = get_user_group_names(request.user)
    highest_group = get_user_highest_privilege_group(request.user)
    
    context = {
        'user_groups': user_groups,
        'highest_group': highest_group,
        'is_super_admin': is_user_in_group(request.user, 'Super Admin'),
        'is_admin': is_user_in_group(request.user, 'Admin'),
        'is_doc_center': is_user_in_group(request.user, 'Documentation Center'),
        'is_member': is_user_in_group(request.user, 'Member'),
    }
    
    return render(request, 'center_panel/group_info.html', context)


@login_required
def group_info_api(request):
    """
    API endpoint to get the user's group information as JSON.
    """
    user_groups = get_user_group_names(request.user)
    highest_group = get_user_highest_privilege_group(request.user)
    
    return JsonResponse({
        'username': request.user.username,
        'user_id': request.user.id,
        'groups': user_groups,
        'highest_group': highest_group,
        'group_memberships': {
            'is_super_admin': is_user_in_group(request.user, 'Super Admin'),
            'is_admin': is_user_in_group(request.user, 'Admin'),
            'is_doc_center': is_user_in_group(request.user, 'Documentation Center'),
            'is_member': is_user_in_group(request.user, 'Member'),
        }
    })


@login_required
def group_protected_view(request):
    """
    Example view that only allows certain groups to access it.
    """
    # Check if user is in allowed groups
    allowed_groups = ['Super Admin', 'Admin']
    if not require_groups(request.user, allowed_groups):
        return render(request, 'center_panel/access_denied.html', {
            'required_groups': allowed_groups,
            'user_groups': get_user_group_names(request.user)
        })
    
    return render(request, 'center_panel/group_protected.html', {
        'user_groups': get_user_group_names(request.user),
        'highest_group': get_user_highest_privilege_group(request.user)
    })
