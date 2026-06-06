from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "organization", "resource_type", "created_at")
    list_filter = ("action", "organization")
    search_fields = ("user__email", "resource_type")
    readonly_fields = ("created_at",)
