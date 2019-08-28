from django.db import models
from django.core.exceptions import ValidationError

from utils.b64id import B64ID, b64id4


class B64IDField(models.UUIDField):
  default_error_messages = {
      'invalid': ("'%(value)s' is not a valid B64ID."),
  }
  description = 'Base64 encoded UUID'

  def __init__(self, verbose_name=None, **kwargs):
    kwargs['max_length'] = 22
    kwargs['default'] = b64id4
    kwargs['editable'] = False
    super().__init__(verbose_name, **kwargs)

  def get_internal_type(self):
    return "UUIDField"

  def get_db_prep_value(self, value, connection, prepared=False):
    if value is None:
      return None
    if not isinstance(value, B64ID):
      value = self.to_python(value)

    if connection.features.has_native_uuid_field:
      return value.as_uuid()
    return value.hex

  def from_db_value(self, value, expression, connection):
    if value is None:
      return value
    return B64ID(value)

  def to_python(self, value):
    if value is not None and not isinstance(value, B64ID):
      try:
        return B64ID(value)
      except (AttributeError, ValueError):
        raise ValidationError(
            self.error_messages['invalid'],
            code='invalid',
            params={'value': value},
        )
    return value

  def formfield(self, **kwargs):
    return None

  @classmethod
  def default_value(cls):
    return b64id4()
