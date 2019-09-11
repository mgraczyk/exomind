from django import forms
from django.db import models, transaction
from django.forms import Form
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

from utils.fields import B64IDField
from app.reviewable import Reviewable


class RangeInput(forms.NumberInput):
  input_type = 'range'


class Review(models.Model):
  id = B64IDField(primary_key=True, editable=False)

  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  reviewable = models.ForeignKey('app.reviewable', on_delete=models.PROTECT)
  name = models.TextField(max_length=200, null=True, blank=True)

  time = models.DateTimeField(auto_now_add=True, editable=False)
  rating = models.FloatField(
      null=True, blank=True, validators=(MinValueValidator(0.), MaxValueValidator(5.)))
  text = models.TextField(max_length=65535, default='', blank=True)

  class Meta:
    unique_together = (('user', 'reviewable'),)

  @classmethod
  def create_or_update(cls, user, data, id):
    with transaction.atomic():
      reviewable = Reviewable.get_or_create(data)
      kwargs = {
          'user': user,
          'reviewable': reviewable,
          'defaults': {
              'name': data.get('name'),
              'rating': data.get('rating'),
              'text': data.get('text', ''),
          }
      }

      # Check for url and user when id is None
      if id:
        kwargs['id'] = id
      if data.get('time'):
        kwargs['defaults']['time'] = data['time']

      return cls.objects.update_or_create(**kwargs)

  @classmethod
  def api_format_from_id(cls, user, review_id):
    return Review.objects.get(user=user, id=review_id).get_api_format()

  @property
  def url(self):
    return self.reviewable.url

  def get_api_format(self):
    return {
        'id': self.id,
        'url': self.reviewable.url,
        'name': self.name,
        'time': self.time,
        'rating': self.rating,
        'text': self.text,
    }
