import os
from django.urls import path

import exomind.crawler_views as cv
from exomind.views import catchall

urlpatterns = [
    path('<path:_>', catchall),
]
