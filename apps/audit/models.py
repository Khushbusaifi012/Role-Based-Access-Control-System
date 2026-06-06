from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
        ("LOGIN_FAILED", "Login Failed"),
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("PERMISSION_CHANGE", "Permission Change"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    organization = models.ForeignKey(
        "rbac.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50, blank=True)
    resource_id = models.IntegerField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        who = self.user.email if self.user else "Anonymous"
        return f"{self.action} by {who} at {self.created_at}"
