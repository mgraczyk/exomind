from django.db import models
from django.forms import ModelForm

from utils.fields import B64IDField


class Reviewable(models.Model):
  id = B64IDField(primary_key=True, editable=False)

  url = models.URLField(max_length=4095, unique=True)
  image_url = models.URLField(max_length=32767, null=True, blank=True)

  @classmethod
  def get_or_create(cls, data):
    return cls.objects.get_or_create(
        url=data['url'],
        defaults={'image_url': data.get('image_url') or None})[0]
