from django.urls import path, register_converter

import app.site as sv
import app.admin as av
from utils.django_helpers import B64IDConverter

register_converter(B64IDConverter, 'b64id')

urlpatterns = [
    path('', sv.home_view, name='home'),
    path('login', sv.login_view, name='login'),
    path('logout', sv.logout_view, name='logout'),
    path('feed', sv.feed_view, name='feed'),
    path('reviews/new', sv.manage_review_view, name='new_review'),
    path('reviews/<b64id:review_id>', sv.manage_review_view, name='manage_review'),
    path('reviews/<b64id:review_id>/edit', sv.full_review_view, name='full_review'),
    path('profiles/<uuid:user_id>', sv.profile_view, name='profile_view'),

    path('admin', av.admin_view, name='admin'),
    path('admin/scrape', av.admin_scrape_view, name='admin_scrape'),
]
