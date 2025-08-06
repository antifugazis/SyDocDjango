from .models import Profile


def profile_processor(request):
    """
    Context processor to add the user's profile to the context of all templates.
    """
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            # Create a profile if it doesn't exist
            profile = Profile.objects.create(user=request.user)
        return {'profile': profile}
    return {}
