from django import forms
from django.db import models, transaction
from django.forms import Form
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

from utils.fields import B64IDField
from app.reviewable import Reviewable



def remove_any_from_start(s, *args):
  for a in args:
    if s.startswith(a):
      return s[len(a):]

  return s


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

  @property
  def url(self):
    return self.reviewable.url

  @property
  def short_url(self):
    return remove_any_from_start(remove_any_from_start(self.url, 'http://', 'https://'),
                                 'www.')[:100]

  def get_api_format(self):
    return {
        'id': self.id,
        'url': self.reviewable.url,
        'name': self.name,
        'time': self.time,
        'rating': self.rating,
        'text': self.text,
    }


class ReviewForm(Form):
  url = forms.URLField(label="URL of the thing you're reviewing", required=True)
  name = forms.CharField(label="Optional Name of the thing you're reviewing", required=False)

  rating = forms.FloatField(
      label='Overall Rating. How interesting was it?',
      required=False,
      min_value=0,
      max_value=5,
      widget=RangeInput(attrs={'step': "0.5"}))

  text = forms.CharField(
      label='Optional summary or thoughts', widget=forms.Textarea, required=False)

  @classmethod
  def from_review_id(cls, user, review_id):
    api_format = Review.objects.get(user=user, id=review_id).get_api_format()
    return cls(api_format)
