from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/tweets/', include('apps.tweets.urls')),
    path('api/search/', include('apps.search.urls')),
]
