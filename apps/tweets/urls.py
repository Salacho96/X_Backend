from django.urls import path
from .views import (
    TweetListCreateView,
    TweetDetailView,
    TimelineView,
    LikeView,
)

urlpatterns = [
    path('', TweetListCreateView.as_view(), name='tweet-list-create'),
    path('<int:pk>/', TweetDetailView.as_view(), name='tweet-detail'),
    path('timeline/', TimelineView.as_view(), name='timeline'),
    path('<int:pk>/like/', LikeView.as_view(), name='like'),
]
