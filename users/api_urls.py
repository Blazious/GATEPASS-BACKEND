from django.urls import path
from .api_views import UserListView, UserDetailView,  CurrentUserView

urlpatterns = [
    path('', UserListView.as_view(), name='api_user_list'),          # List all users
    path('<int:pk>/', UserDetailView.as_view(), name='api_user_detail'),
    path('me/', CurrentUserView.as_view(), name='api_user_current'),  # Get user detail
]
