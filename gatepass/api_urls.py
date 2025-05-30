from django.urls import path
from .api_views import MyGatepassRequestsView, ApproveGatepassView, download_gatepass_pdf



urlpatterns = [
    path('requests/', MyGatepassRequestsView.as_view(), name='api_my_requests'),
    path('approve/<int:pk>/', ApproveGatepassView.as_view(), name='api_approve_gatepass'),
    path('<int:pk>/download/', download_gatepass_pdf, name='download_gatepass_pdf'),
    
]
