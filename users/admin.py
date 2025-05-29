from django.contrib import admin
from .models import User, Department
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'name', 'role', 'department', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'department')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'department', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'department', 'role', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(Department)
