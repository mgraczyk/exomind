from django.core.management.base import BaseCommand

from app.fill_missing import fill_missing_review_data


class Command(BaseCommand):
  help = 'Fill missing data in reviews by scraping sites'

  def add_arguments(self, parser):
    pass

  def handle(self, *args, **options):
    fill_missing_review_data(None)
