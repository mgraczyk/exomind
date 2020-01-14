from urllib.parse import urlparse
from collections import defaultdict

from app.review import Review


def compute_stats_for_profile(user_id):
  user_reviews = Review.objects.filter(user_id=user_id).values('rating', 'reviewable__url')

  reviews_by_host = defaultdict(list)
  for r in user_reviews:
    parsed_url = urlparse(r['reviewable__url'])
    host = parsed_url.netloc
    r['host'] = host
    reviews_by_host[host].append(r)

  host_breakdown_items = []
  for host, reviews in reviews_by_host.items():
    host_breakdown_items.append({
        'host': host,
        'num_reviews': len(reviews),
        'avg_rating': sum(r['rating'] for r in reviews) / len(reviews),
    })

  return {
      'host_breakdown':
          sorted(host_breakdown_items, key=lambda item: item["num_reviews"], reverse=True),
  }
