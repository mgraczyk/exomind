from django.db import models, transaction, connection
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

from common.util import AttributeDict, lazy_property
from utils.b64id import B64ID
from utils.fields import B64IDField
from app.reactions import Reaction
from app.reviewable import Reviewable
from app.users import User


def annotate_obj(obj, **kwargs):
  for k, v in kwargs.items():
    setattr(obj, k, v)
  return obj


def replace_uuid_recursively(obj):
  if isinstance(obj, (list, tuple)):
    for v in obj:
      replace_uuid_recursively(v)
  elif isinstance(obj, dict):
    updates = {}
    for k, v in obj.items():
      replace_uuid_recursively(v)
      if k.endswith('id'):
        updates[k] = None if v is None else B64ID(v)
    obj.update(updates)

  return obj


def maybe_uuid(x):
  return x.as_uuid() if x else x


class ReviewManager(models.Manager):

  def get_queryset(self):
    # TODO: Add reactions.
    return super().get_queryset().select_related('user', 'reviewable')

  def with_me_data(self, me_id=None, user_id=None, id=None, limit=None, offset=None, order_by=None):
    review_table = 'app_review'
    user_table = 'app_user'
    reviewable_table = 'app_reviewable'
    reaction_table = 'app_reaction'
    comment_table = 'app_comment'

    table_cols = {
        review_table: ('id', 'name', 'time', 'rating', 'text'),
        user_table: ('id', 'email', 'username'),
        reviewable_table: ('id', 'url', 'image_url'),
        'me_data': ('reaction_type',),
        'reaction_data': ('explicit',),
        'comments': ('explicit',),
    }
    table_cols_flat = [(table, col) for table, cols in table_cols.items() for col in cols]
    select_cols = ','.join(f'{table}.{col}' for table, col in table_cols_flat)
    maybe_where_user = f'AND {review_table}.user_id=%(user_id)s' if user_id else ''
    maybe_where_review = f'AND {review_table}.id=%(id)s' if id else ''
    maybe_where_entity_has_id = f'WHERE entity_id=%(id)s' if id else ''

    maybe_order_by = f'ORDER BY {order_by}' if order_by else f'ORDER BY {review_table}.time DESC'
    maybe_limit = f'LIMIT {limit}' if limit else ''
    maybe_offset = f'OFFSET {offset}' if offset else ''

    query = f"""
        SELECT {select_cols} FROM {review_table}
        LEFT JOIN {user_table} on {user_table}.id={review_table}.user_id
        LEFT JOIN {reviewable_table} on {reviewable_table}.id={review_table}.reviewable_id
        LEFT OUTER JOIN (
          SELECT entity_id, type as reaction_type
          FROM {reaction_table}
          WHERE user_id=%(me_id)s
        ) me_data on me_data.entity_id={review_table}.id
        LEFT OUTER JOIN (
          SELECT
            entity_id,
            json_agg(json_build_object(
              'user_id', {user_table}.id,
              'username', {user_table}.username,
              'type', {reaction_table}.type
            )) as explicit
          FROM {reaction_table}
          JOIN {user_table} on {reaction_table}.user_id={user_table}.id
          {maybe_where_entity_has_id}
          GROUP BY entity_id
        ) reaction_data on reaction_data.entity_id={review_table}.id
        LEFT OUTER JOIN (
          SELECT
            entity_id,
            json_agg(json_build_object(
              'id', {comment_table}.id,
              'user_id', {user_table}.id,
              'username', {user_table}.username,
              'text', {comment_table}.text,
              'created_at', {comment_table}.created_at,
              'in_reply_to_id', {comment_table}.in_reply_to_id
            )) as explicit
          FROM {comment_table}
          JOIN {user_table} on {comment_table}.user_id={user_table}.id
          {maybe_where_entity_has_id}
          GROUP BY entity_id
        ) comments on comments.entity_id={review_table}.id
        WHERE true
          {maybe_where_user}
          {maybe_where_review}
        {maybe_order_by}
        {maybe_limit}
        {maybe_offset}
    """

    with connection.cursor() as cursor:
      cursor.execute(query, {
          'me_id': maybe_uuid(me_id),
          'user_id': maybe_uuid(user_id),
          'id': maybe_uuid(id)
      })
      rows = list(cursor.fetchall())

    table_col_to_row = {p: i for i, p in enumerate(table_cols_flat)}
    row_data = [{
        table: replace_uuid_recursively({col: row[table_col_to_row[table, col]]
                                         for col in cols})
        for table, cols in table_cols.items()
    } for row in rows]

    results = [
        annotate_obj(
            Review(
                **data[review_table],
                user=User(**data[user_table]),
                reviewable=Reviewable(**data[reviewable_table])),
            me=data['me_data'],
            reaction_data=data['reaction_data'],
            comments=data['comments']) for data in row_data
    ]

    return results


class Review(models.Model):
  objects = ReviewManager()

  id = B64IDField(primary_key=True, editable=False)

  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  reviewable = models.ForeignKey('app.reviewable', on_delete=models.PROTECT)

  name = models.TextField(max_length=200, default='', blank=True)
  time = models.DateTimeField(auto_now_add=True, editable=False)
  rating = models.FloatField(
      null=True, blank=True, validators=(MinValueValidator(0.), MaxValueValidator(5.)))
  text = models.TextField(max_length=65535, default='', blank=True)

  class Meta:
    unique_together = (('user', 'reviewable'),)

  @classmethod
  def create_or_update(cls, user, data, id):
    with transaction.atomic():
      if user.is_admin:
        # TODO: Do not special case admins here.
        reviewable, _ = Reviewable.update_or_create(data)
      else:
        reviewable, _ = Reviewable.get_or_create(data)

      kwargs = {
          'user': user,
          'defaults': {
              'name': data.get('name'),
              'rating': None if data.get('no_rating') == 'on' else data.get('rating'),
              'text': data.get('text', ''),
          }
      }

      # Check for url and user when id is None
      if id:
        kwargs['id'] = id
        kwargs['defaults']['reviewable'] = reviewable
      else:
        kwargs['reviewable'] = reviewable

      if data.get('time'):
        kwargs['defaults']['time'] = data['time']

      return cls.objects.update_or_create(**kwargs)

  @property
  def url(self):
    return self.reviewable.url

  @property
  def image_url(self):
    return self.reviewable.image_url

  @lazy_property
  def reaction_data(self):
    raise NotImplementedError()

  @lazy_property
  def me_data(self):
    return AttributeDict(
        reaction_type=Reaction.objects.filter(user_id=self.user_id, entity_id=self.id).first())
