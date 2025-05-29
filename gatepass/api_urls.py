from django.urls import path
from .api_views import MyGatepassRequestsView, ApproveGatepassView

urlpatterns = [
    path('requests/', MyGatepassRequestsView.as_view(), name='api_my_requests'),
    path('approve/<int:pk>/', ApproveGatepassView.as_view(), name='api_approve_gatepass'),
]
