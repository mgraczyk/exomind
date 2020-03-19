from urllib.parse import urlparse
from collections import defaultdict

from app.review import Review


def compute_stats_for_profile(me_id, user_id):
  user_reviews = Review.objects.with_me_data(
      me_id=me_id, user_id=user_id, order_by='rating DESC, time DESC')

  reviews_by_host = defaultdict(list)
  for r in user_reviews:
    parsed_url = urlparse(r.url)
    host = parsed_url.netloc
    r.host = host
    reviews_by_host[host].append(r)

  host_breakdown_items = []
  for host, reviews in reviews_by_host.items():
    reviews_with_rating = [r for r in reviews if r is not None]
    host_breakdown_items.append({
        'host': host,
        'num_reviews': len(reviews),
        'avg_rating': sum(r.rating for r in reviews_with_rating) / len(reviews_with_rating),
    })

  return {
      'host_breakdown':
          sorted(host_breakdown_items, key=lambda item: item["num_reviews"], reverse=True),
      'top_reviews': user_reviews[:5],
  }
