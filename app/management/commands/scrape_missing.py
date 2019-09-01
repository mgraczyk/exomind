import os
from tqdm import tqdm
from django.core.management.base import BaseCommand

from utils.scrape_meta import get_good_title_for_page
from app.models import Review


class Command(BaseCommand):
  help = 'Fill missing data in reviews by scraping sites'

  def add_arguments(self, parser):
    pass

  def handle(self, *args, **options):
    reviews_without_name = list(
        Review.objects.select_related('reviewable').filter(name__isnull=True))

    print('adding names to {} reviews'.format(len(reviews_without_name)))

    for review in tqdm(reviews_without_name):
      good_title = get_good_title_for_page(review.url)
      review.name = good_title
      review.save(update_fields=['name'])
