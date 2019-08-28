from django.urls import path, include

urlpatterns = [
    path('social/', include('social_django.urls')),
    path('', include('app.urls')),
]
