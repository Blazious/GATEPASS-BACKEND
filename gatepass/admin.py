from django.contrib import admin
from .models import GatepassRequest

class GatepassRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'department', 'status',
        'exit_time', 'return_time',
        'department_approver', 'security_approver'
    )
    list_filter = ('status', 'department')
    search_fields = ('user__name', 'reason', 'comments')

admin.site.register(GatepassRequest, GatepassRequestAdmin)
