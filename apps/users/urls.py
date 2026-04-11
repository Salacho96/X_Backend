from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    FollowView,
    FollowersListView,
    FollowingListView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/follow/', FollowView.as_view(), name='follow'),
    path('profile/<str:username>/followers/', FollowersListView.as_view(), name='followers'),
    path('profile/<str:username>/following/', FollowingListView.as_view(), name='following'),
]