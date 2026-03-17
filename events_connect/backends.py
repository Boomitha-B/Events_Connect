from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailAuthBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # We assume 'username' parameter contains the 'email' from the form
        try:
            # Look up the user by email
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Fail-safe in case multiple users share an email (should be prevented by DB constraints)
            user = User.objects.filter(email=username).order_by('id').first()
            if user.check_password(password):
                return user
        return None
