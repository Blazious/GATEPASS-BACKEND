from django.urls import path
from .api_views import UserListView, UserDetailView

urlpatterns = [
    path('', UserListView.as_view(), name='api_user_list'),          # List all users
    path('<int:pk>/', UserDetailView.as_view(), name='api_user_detail'),  # Get user detail
]
