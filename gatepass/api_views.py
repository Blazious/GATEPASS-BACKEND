from rest_framework import generics, permissions
from .models import GatepassRequest
from .serializers import GatepassRequestSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status


User = get_user_model()

class MyGatepassRequestsView(generics.ListCreateAPIView):
    serializer_class = GatepassRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Department head sees gatepasses from their department that are pending
        if user.role == 'department_head':
            return GatepassRequest.objects.filter(
                department=user.department,
                status='pending_department'
            )

        # Security head sees gatepasses that are approved by department but pending security
        elif user.role == 'security_head':
            return GatepassRequest.objects.filter(
                status='pending_security'
            )

        # Employee sees only their own gatepass requests
        return GatepassRequest.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, department=self.request.user.department)


class ApproveGatepassView(generics.UpdateAPIView):
    queryset = GatepassRequest.objects.all()
    serializer_class = GatepassRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        decision = request.data.get("decision")  # "approve" or "reject"

        if not decision:
            return Response({"detail": "Decision (approve or reject) is required."}, status=status.HTTP_400_BAD_REQUEST)

        if user.role == 'department_head' and instance.status == 'pending_department':
           if decision == 'approve':
                instance.status = 'pending_security'
                instance.department_approver = user
                instance.department_approval_date = timezone.now()
           elif decision == 'reject':
                instance.status = 'rejected_department'
                instance.department_approver = user
                instance.department_approval_date = timezone.now()
        elif user.role == 'security_head' and instance.status == 'pending_security':
            if decision == 'approve':
                instance.status = 'approved_security'
                instance.security_approver = user
                instance.security_approval_date = timezone.now()
            elif decision == 'reject':
                instance.status = 'rejected_security'
                instance.security_approver = user
                instance.security_approval_date = timezone.now()

        else:
            return Response({"detail": "Invalid role or gatepass state for this action."}, status=status.HTTP_403_FORBIDDEN)        

        instance.save()
        return self.update(request, *args, **kwargs,partial=True)
