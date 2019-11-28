from django.db import models
from django.conf import settings

from utils.fields import B64IDField


class Reaction(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  entity_id = B64IDField()

  type = models.PositiveSmallIntegerField(default=0)
