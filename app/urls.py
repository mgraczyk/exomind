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
    path('reviews/<b64id:review_id>/edit', sv.manage_review_view, name='manage_review'),
    path('reviews/<b64id:review_id>', sv.full_review_view, name='full_review'),
    path('reviews/<b64id:review_id>/react', sv.react_to_review_view, name='react_to_review'),
    path('reviews/<b64id:review_id>/comment', sv.comment_on_review_view, name='comment_on_review'),
    path('reviews/<b64id:review_id>/comment/<b64id:comment_id>/delete', sv.delete_comment_view, name='delete_comment'),
    path('reviews/<b64id:review_id>/comment/<b64id:comment_id>/react', sv.react_to_comment_view, name='react_to_comment'),
    path('reviews/search', sv.review_search_view, name='review_search'),
    path('profiles/<b64id:user_id>', sv.profile_view, name='profile_view'),
    path('admin', av.admin_view, name='admin'),
    path('admin/scrape', av.admin_scrape_view, name='admin_scrape'),
]
