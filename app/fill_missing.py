from tqdm import tqdm

from utils.scrape_meta import get_good_image_for_page, get_good_title_for_page
from app.models import Review, Reviewable


def maybe_filter(x, **kwargs):
  if kwargs and any(kwargs.values()):
    return x.filter(**kwargs)
  return x


def fill_missing_review_data(review_id):
  reviews_without_name = list(
      maybe_filter(
          Review.objects.select_related('reviewable').filter(name__isnull=True),
          id=review_id))

  print('adding names to {} reviews'.format(len(reviews_without_name)))

  for review in tqdm(reviews_without_name):
    good_title = get_good_title_for_page(review.url)
    review.name = good_title
    review.save(update_fields=['name'])

  reviewables_without_image = list(
      maybe_filter(
          Reviewable.objects.filter(image_url__isnull=True),
          review__id=review_id))

  print('adding images to {} reviewables'.format(
      len(reviewables_without_image)))
  for reviewable in tqdm(reviewables_without_image):
    good_image = get_good_image_for_page(reviewable.url)
    if good_image:
      reviewable.image_url = good_image
      reviewable.save(update_fields=['image_url'])
