# backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CaseInsensitiveModelBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
          user = UserModel.objects.get(username__iexact=username)
          if user.check_password(password):
            return user
          else:
            return None
        except UserModel.DoesNotExist:
          # Run the default password hasher once to reduce the timing
          # difference between an existing and a non-existing user (#20760).
          UserModel().set_password(password)
          return None
        
    