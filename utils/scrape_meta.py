import requests
from bs4 import BeautifulSoup
from collections import defaultdict


class PageCache(dict):

  @classmethod
  def fetch_content(cls, url, context=None):
    if context and url in context:
      return context[url]

    r = requests.get(url, allow_redirects=True)
    r.raise_for_status()
    if context:
      context[url] = r.content

    return r.content


def get_meta_for_page(url, context=None):
  soup = BeautifulSoup(
      PageCache.fetch_content(url, context), features='html.parser')

  title_tag = soup.find("title")
  title = title_tag.text if title_tag else ''

  meta_tags = soup.find_all("meta")
  meta_by_property = {tag.attrs.get('property'): tag for tag in meta_tags}

  meta = defaultdict(str, {
      'title': title,
  })
  meta.update({
      k: meta_by_property[k].attrs.get('content')
      for k in ('og:title', 'og:image')
      if k in meta_by_property
  })

  return meta


def get_good_title_for_page(url, context=None):
  meta = get_meta_for_page(url, context)

  if meta['og:title'] and len(meta['og:title']) > len(meta['title']):
    return meta['og:title']
  else:
    return meta['title']


def get_good_image_for_page(url, context=None):
  meta = get_meta_for_page(url, context)
  return meta['og:image']
