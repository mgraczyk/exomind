from django.contrib.auth import get_user_model

UserModel = get_user_model()


class JWTBackend:

  def authenticate(self, request, username=None, password=None, **kwargs):
    print('authing')
    return None

  def user_can_authenticate(self, user):
    print('checking can auth')
    return user.is_active

  def get_user(self, user_id):
    try:
      user = UserModel._default_manager.get(pk=user_id)
    except UserModel.DoesNotExist:
      return None
    return user if self.user_can_authenticate(user) else None
