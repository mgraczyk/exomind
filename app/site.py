from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.shortcuts import render

from app.users import User
from app.review import Review

CREATE_OR_UPDATE_METHODS = {'POST', 'PUT', 'PATCH'}


def render_with_globals(request, template, context):
  context['me'] = request.user
  return render(request, template, context)


def home_view(request):
  return feed_view(request)


def login_view(request):
  context = {}
  return render_with_globals(request, 'login.html', context)


def logout_view(request):
  logout(request)
  return HttpResponseRedirect('/')


def manage_review_view(request, review_id=None):
  if request.method in CREATE_OR_UPDATE_METHODS:
    data = request.POST
    review, _ = Review.create_or_update(request.user, data, id=review_id)
    return HttpResponseRedirect('/?submittedReview={}'.format(review.id))
  else:
    if review_id:
      review = Review.api_format_from_id(request.user, review_id)
    else:
      # pre-populate fields from url parameters.
      review = {k: v for k, v in request.GET.items() if k in {'url', 'rating', 'text'}}

  return render_with_globals(request, 'manage_review.html', {'review': review, 'review_id': review_id})


def profile_view(request, user_id, review_id=None):
  context = {
      'reviews': Review.objects.filter(user_id=user_id).order_by('-time'),
      'profile_user': User.objects.get(id=user_id),
  }
  return render_with_globals(request, 'profile.html', context)


def full_review_view(request, review_id):
  context = {
      'review': Review.objects.get(id=review_id),
  }
  return render_with_globals(request, 'full_review.html', context)


def feed_view(request):
  context = {
      'reviews': Review.objects.select_related('user').order_by('-time'),
  }
  return render_with_globals(request, 'feed.html', context)
