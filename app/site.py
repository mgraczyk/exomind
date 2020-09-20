from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib.auth import logout
from django.shortcuts import render

from app.fill_missing import fill_missing_review_data
from app.users import User
from app.profile import compute_stats_for_profile
from app.reactions import Reaction
from app.comment import Comment
from app.review import Review
from utils import AttributeDict

CREATE_OR_UPDATE_METHODS = {'POST', 'PUT', 'PATCH'}
DEFAULT_LIMIT = 50


def int_or_none(x):
  try:
    return int(x)
  except (ValueError, TypeError):
    return None


def parse_pagination_params(request):
  return {
      'limit': int_or_none(request.GET.get('limit')) or DEFAULT_LIMIT,
      'offset': int_or_none(request.GET.get('offset')) or 0,
  }


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
      review = AttributeDict(
          {k: v
           for k, v in request.GET.items()
           if k in {'url', 'rating', 'text'}})

  return render_with_globals(request, 'manage_review.html', {
      'review': review,
      'review_id': review_id
  })


def profile_view(request, user_id, review_id=None):
  pagination = parse_pagination_params(request)

  stats = compute_stats_for_profile(request.user.id, user_id)

  context = {
      'reviews': Review.objects.with_me_data(me_id=request.user.id, user_id=user_id, **pagination),
      'profile_user': User.objects.get(id=user_id),
      'stats': stats,
      'pagination': pagination,
  }
  return render_with_globals(request, 'profile.html', context)


def full_review_view(request, review_id):
  context = {
      'review': Review.objects.with_me_data(me_id=request.user.id, id=review_id)[0],
  }
  return render_with_globals(request, 'full_review.html', context)


def feed_view(request):
  pagination = parse_pagination_params(request)

  context = {
      'reviews': Review.objects.with_me_data(me_id=request.user.id, **pagination),
      'pagination': pagination,
  }

  return render_with_globals(request, 'feed.html', context)


def review_search_view(request):
  q = request.GET.get('q')
  if q:
    q_search = q.lower()
    reviews = Review.objects.with_me_data(me_id=request.user.id)
    filtered_reviews = [r for r in reviews if q_search in ' '.join((r.name, r.url, r.text)).lower()]
  else:
    filtered_reviews = []

  context = {
      'reviews': filtered_reviews[:DEFAULT_LIMIT],
      'q': q,
  }

  return render_with_globals(request, 'review_search.html', context)


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


def react_to_comment_view(request, review_id, comment_id):
  if request.user.id is None:
    return HttpResponseRedirect('/login')

  with transaction.atomic():
    my_reactions_query = Reaction.objects.filter(user_id=request.user.id, entity_id=comment_id)
    if my_reactions_query.exists():
      my_reactions_query.delete()
    else:
      my_reactions_query.update_or_create(
          user_id=request.user.id, entity_id=review_id, defaults={"type": 1})

  next_url = f'/reviews/{review_id}?likedComment={comment_id}'

  return HttpResponseRedirect(next_url)


def comment_on_review_view(request, review_id):
  if request.user.id is None:
    return HttpResponseRedirect('/login')

  if request.method != 'POST':
    raise HttpResponseForbidden()

  data = request.POST
  if not data.get('text'):
    # Just send them back to the review page.
    return full_review_view(request, review_id)

  created_comment = Comment.objects.create(
      user_id=request.user.id, entity_id=review_id, text=data.get('text'), in_reply_to=None)

  next_url = f'/reviews/{review_id}?created_comment_id={created_comment.id}'
  return HttpResponseRedirect(next_url)


def delete_comment_view(request, review_id, comment_id):
  if request.user.id is None:
    return HttpResponseRedirect('/login')

  if request.method != 'POST':
    raise HttpResponseForbidden()

  deleted = Comment.objects.filter(
      user_id=request.user.id, entity_id=review_id, id=comment_id).delete()

  next_url = f'/reviews/{review_id}'
  return HttpResponseRedirect(next_url)
