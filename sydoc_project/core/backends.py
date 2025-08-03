from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in with either
    their username or email address.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by username or email
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user.
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Handle case where multiple users have the same email
            # This should not happen in a properly configured system
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                # Log user login with group information
                self.log_user_login(user)
                return user
        return None
    
    def log_user_login(self, user):
        """
        Log user login with their group information.
        """
        import logging
        logger = logging.getLogger('auth')
        
        # Get user groups
        user_groups = list(user.groups.values_list('name', flat=True))
        
        logger.info(f"User '{user.username}' (ID: {user.id}) logged in. Groups: {user_groups}")
