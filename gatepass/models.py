from django.db import models
from users.models import User, Department

# Created your models here.
class GatepassRequest(models.Model):
    STATUS_CHOICES = [
        ('pending_department', 'Pending Department Approval'),
        ('approved_department', 'Approved by Department'),
        ('rejected_department', 'Rejected by Department'),
        ('pending_security', 'Pending Security Approval'),
        ('approved_security', 'Approved by Security'),
        ('rejected_security', 'Rejected by Security'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gatepass_requests')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField()
    date_requested = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField()
    return_time = models.DateTimeField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_department')
    
    department_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dept_approvals')
    department_approval_date = models.DateTimeField(null=True, blank=True)
    
    security_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='security_approvals')
    security_approval_date = models.DateTimeField(null=True, blank=True)
    
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"Gatepass #{self.id} by {self.user.name} - {self.status}"
    
    #Gatepass item added 
class GatepassItem(models.Model):
    gatepass = models.ForeignKey(GatepassRequest, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.item_name} x{self.quantity}"

  
