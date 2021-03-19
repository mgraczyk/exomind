import os
import json
from django.conf import settings
from django.shortcuts import get_object_or_404, render

_COMPANY_NAME = os.getenv('COMPANY_NAME') or 'exomind'

def shorten(x):
    if not x:
        return ''

    if len(x) > 40:
        return x[:40].rstrip() + '...'
    else:
        return x

def render_crawler_page(request, params):
    return render(
        request, 'crawler_page.html', {
            'page_title': _COMPANY_NAME,
            'og_url': settings.CLIENT_URL.rstrip('/') + request.path,
            'facebook_app_id': os.getenv('FACEBOOK_APP_ID'),
            'og_type': 'website',
            **params,
        })
