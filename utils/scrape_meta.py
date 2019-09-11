import requests
from bs4 import BeautifulSoup


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

  title = soup.find("title").text
  meta_tags = soup.find_all("meta")
  meta_by_property = {tag.attrs.get('property'): tag for tag in meta_tags}

  meta = {
      'title': title,
  }
  meta.update({
      k: meta_by_property[k].attrs.get('content')
      for k in ('og:title', 'og:image')
      if k in meta_by_property
  })

  return meta


def get_good_title_for_page(url, context=None):
  meta = get_meta_for_page(url, context)
  if len(meta.get('title', '')) < len(meta.get('og:title', '')):
    return meta.get('title', '')
  else:
    return meta.get('og:title', '')


def get_good_image_for_page(url, context=None):
  meta = get_meta_for_page(url, context)
  return meta.get('og:image')
