import uuid
from django.db import models, IntegrityError
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.postgres.fields.citext import CIEmailField, CITextField

from utils.fields import B64IDField


class UserManager(BaseUserManager):

  def create_user(self, *args, **kwargs):
    email = self.normalize_email(kwargs['email'])
    try:
      return User.objects.create(email=email, username=kwargs['username'])
    except IntegrityError:
      # Without username.
      return User.objects.get(email=email)

  def create_superuser(*args, **kwargs):
    raise Exception('no superusers allowed')


class User(AbstractBaseUser):
  EMAIL_FIELD = 'email'
  USERNAME_FIELD = 'username'

  id = B64IDField(primary_key=True, editable=False)
  email = CIEmailField(max_length=255, unique=True)
  username = CITextField(max_length=255, unique=True)

  is_active = True

  objects = UserManager()

  @property
  def is_admin(self):
    # TODO(mgraczyk): Fix
    return self.email.lower() == 'michael@mgraczyk.com'
