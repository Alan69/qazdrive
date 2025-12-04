from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from userconf.models import User


class PhoneOrEmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using either:
    - Phone number
    - Email address
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by phone_number or email
            user = User.objects.get(
                Q(phone_number=username) | Q(email=username)
            )
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing
            # difference between existing and non-existing users
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # This shouldn't happen with proper unique constraints
            return None
        
        # Check password and if user is active
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

