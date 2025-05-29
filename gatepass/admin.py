from django.contrib import admin
from .models import GatepassRequest, GatepassItem  # Import both models

class GatepassItemInline(admin.TabularInline):  # or admin.StackedInline if you prefer vertical layout
    model = GatepassItem
    extra = 1  # Number of empty item forms to show by default

class GatepassRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'department', 'status',
        'exit_time', 'return_time',
        'department_approver', 'security_approver'
    )
    list_filter = ('status', 'department')
    search_fields = ('user__name', 'reason', 'comments')
    inlines = [GatepassItemInline]  # Add inline item editor

admin.site.register(GatepassRequest, GatepassRequestAdmin)

# Optional: Register GatepassItem separately if you want to view/manage them on their own
admin.site.register(GatepassItem)

