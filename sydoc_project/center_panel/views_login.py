from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .views import get_redirect_url_for_user


@login_required
def login_success(request):
    """
    Redirect user based on their group membership after login.
    """
    # Get the appropriate redirect URL for this user
    redirect_url = get_redirect_url_for_user(request.user)
    
    # Add a welcome message
    user_groups = list(request.user.groups.values_list('name', flat=True))
    if user_groups:
        messages.success(request, f"Bienvenue {request.user.username}! Vous êtes connecté en tant que {', '.join(user_groups)}.")
    else:
        messages.info(request, f"Bienvenue {request.user.username}! Vous n'êtes associé à aucun groupe.")
    
    return redirect(redirect_url)
