from django import template
from django.utils.safestring import mark_safe
from django.utils.html import urlize as urlize_impl
from django.utils.html import escape

register = template.Library()


def remove_any_from_start(s, *args):
  for a in args:
    if s.startswith(a):
      return s[len(a):]

  return s


@register.filter(is_safe=True)
def nice_urlize(value, limit=None):
  escaped_value = escape(value)
  text = remove_any_from_start(
      remove_any_from_start(escaped_value, 'http://', 'https://'), 'www.')
  if limit and len(text) > limit:
    text = '%s...' % text[:int(limit)]

  return mark_safe('<a href="%s" target="_blank" rel="noopener ugc"/>%s</a>' %
                   (escaped_value, text))

@register.filter(is_safe=True)
def star_string(value):
  double_value = int(2 * min(10., max(0., float(value))))

  return '{}{}{}'.format('star ' * (double_value // 2),
                         'star_half ' if double_value % 2 else '',
                         'star_border ' * (5 - (double_value + 1) // 2))