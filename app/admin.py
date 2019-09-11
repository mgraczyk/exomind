from django.http import HttpResponseRedirect

from app.site import render_with_globals
from app.fill_missing import fill_missing_review_data


def admin_view(request):
  return render_with_globals(request, 'admin.html', {})


def admin_scrape_view(request):
  review_id = request.POST.get('review_id')
  fill_missing_review_data(review_id)
  return HttpResponseRedirect('/admin')
