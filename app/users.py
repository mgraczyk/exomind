import uuid
from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.postgres.fields.citext import CIEmailField


class UserManager(BaseUserManager):

  def create_user(self, *args, **kwargs):
    email = self.normalize_email(kwargs['email'])
    return User.objects.create(email=email, username=kwargs['username'])

  def create_superuser(*args, **kwargs):
    raise Exception('no superusers allowed')


class User(AbstractBaseUser):
  EMAIL_FIELD = 'email'
  USERNAME_FIELD = 'username'

  id = models.UUIDField(primary_key=True, default=uuid.uuid4)
  email = CIEmailField(max_length=255, unique=True)
  username = CIEmailField(max_length=255, unique=True)

  is_active = True

  objects = UserManager()

  @property
  def is_admin(self):
    # TODO(mgraczyk): Fix
    return self.email.lower() == 'michael@mgraczyk.com'
