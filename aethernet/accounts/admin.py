from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_superuser', 'is_approved', 'is_active')
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True, is_active=True)

    approve_users.short_description = "Approve and activate selected users"

