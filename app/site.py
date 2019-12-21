from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.shortcuts import render

from app.fill_missing import fill_missing_review_data
from app.users import User
from app.reactions import Reaction
from app.review import Review
from utils import AttributeDict

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
  if not request.user.id:
    return HttpResponseRedirect('/login')

  if request.method in CREATE_OR_UPDATE_METHODS:
    data = request.POST
    if data.get('action') == 'delete':
      Review.objects.filter(user=request.user, id=review_id).delete()
      next_url = '/'
    elif data.get('action') == 'autofill':
      fill_missing_review_data(review_id)
      next_url = request.path
    else:
      review, created = Review.create_or_update(request.user, data, id=review_id)
      if created:
        fill_missing_review_data(review.id)
      next_url = '/?submittedReview={}'.format(review.id)

    return HttpResponseRedirect(next_url)
  else:
    if review_id:
      review = Review.objects.get(user=request.user, id=review_id)
    else:
      # pre-populate fields from url parameters.
      review = AttributeDict({
          k: v
          for k, v in request.GET.items()
          if k in {'url', 'rating', 'text'}
      })

  return render_with_globals(request, 'manage_review.html', {
      'review': review,
      'review_id': review_id
  })


def profile_view(request, user_id, review_id=None):
  context = {
      'reviews': Review.objects.with_me_data(user_id=user_id),
      'profile_user': User.objects.get(id=user_id),
  }
  return render_with_globals(request, 'profile.html', context)


def full_review_view(request, review_id):
  context = {
      'review': Review.objects.with_me_data(id=review_id)[0],
  }
  return render_with_globals(request, 'full_review.html', context)


def feed_view(request):
  context = {
      'reviews': Review.objects.with_me_data(me_id=request.user.id),
  }

  return render_with_globals(request, 'feed.html', context)

def react_to_review_view(request, review_id):
  if request.user.id is None:
    return HttpResponseRedirect('/login')

  with transaction.atomic():
    my_reactions_query = Reaction.objects.filter(user_id=request.user.id, entity_id=review_id)
    if my_reactions_query.exists():
      my_reactions_query.delete()
    else:
      my_reactions_query.update_or_create(
          user_id=request.user.id, entity_id=review_id, defaults={"type": 1})

  if request.GET.get('full'):
    next_url = f'/reviews/{review_id}'
  else:
    next_url = f'/?likedReview={review_id}'

  return HttpResponseRedirect(next_url)
