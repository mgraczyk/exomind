import re
from django.urls import set_urlconf

_SHARE_CRAWLER_UA = re.compile((
    r'facebookexternalhit|Facebot|Slackbot-LinkExpanding|Googlebot|Twitterbot|'
    r'BingPreview|Yahoo Link Preview|Google Web Preview|SkypeUriPreview|LinkedInBot|'
    r'Quora Link Preview|Google-Structured-Data-Testing-Tool|Google-StructuredDataTestingTool'
))


class CrawlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if _SHARE_CRAWLER_UA.match(request.META.get('HTTP_USER_AGENT', '')):
            set_urlconf('exomind.crawler_urls')
            request.urlconf = 'exomind.crawler_urls'
        return self.get_response(request)
