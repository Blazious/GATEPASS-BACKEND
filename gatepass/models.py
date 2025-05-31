from django.db import models
from django.utils.crypto import get_random_string
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
    gatepass = models.ForeignKey('GatepassRequest', on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # New field to indicate if it's a custom/unregistered item
    is_custom = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.item_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        # Auto-generate serial number if not custom and not already set
        if not self.serial_number and not self.is_custom:
            self.serial_number = self.generate_internal_serial()
        super().save(*args, **kwargs)

    def generate_internal_serial(self):
        # Generates something like ECSM-7FJ4X9QD
        unique_part = get_random_string(length=8, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        return f"ECSM-{unique_part}"
  
