from django.db import models
from django.conf import settings

from utils.fields import B64IDField


class Comment(models.Model):
  id = B64IDField(primary_key=True, editable=False)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  entity_id = B64IDField()

  text = models.TextField(default='')
  created_at = models.DateTimeField(auto_now_add=True)
  in_reply_to = models.ForeignKey('app.Comment', null=True, blank=True, on_delete=models.PROTECT)
