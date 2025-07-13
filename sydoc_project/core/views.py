from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile

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
