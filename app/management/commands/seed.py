import os
from django.core.management.base import BaseCommand

from app.models import User, Review
from test.utils import csv_to_json


class Command(BaseCommand):
  help = 'Seed some data'

  def add_arguments(self, parser):
    pass

  def handle(self, *args, **options):
    reviews = csv_to_json(
        os.path.join(os.path.dirname(__file__), '../../../test/data/reviews.csv'))

    user, _ = User.objects.get_or_create(
        email='michael@mgraczyk.com', defaults={'username': 'Michael'})
    for review in reviews:
      Review.create_or_update(user, review, None)
