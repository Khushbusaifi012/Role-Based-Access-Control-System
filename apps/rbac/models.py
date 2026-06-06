from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Feature(models.Model):
    """System-wide feature flags that can be toggled per role."""

    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)
    module = models.CharField(max_length=50, default="general")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["module", "code"]

    def __str__(self):
        return f"{self.code} ({self.name})"


class Role(models.Model):
    """Default roles (organization=null) or custom org-specific roles."""

    name = models.CharField(max_length=100)
    slug = models.SlugField()
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="roles",
    )
    is_default = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("slug", "organization")]
        ordering = ["name"]

    def __str__(self):
        prefix = self.organization.name if self.organization else "System"
        return f"{self.name} ({prefix})"

    def has_feature(self, feature_code):
        perm = self.permissions.filter(feature__code=feature_code, is_enabled=True).first()
        return perm is not None

    def get_enabled_features(self):
        return list(
            self.permissions.filter(is_enabled=True).values_list("feature__code", flat=True)
        )


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name="role_permissions")
    is_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = [("role", "feature")]

    def __str__(self):
        status = "ON" if self.is_enabled else "OFF"
        return f"{self.role.name} -> {self.feature.code} [{status}]"


class Membership(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="memberships")
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "organization")]

    def __str__(self):
        return f"{self.user.email} @ {self.organization.name} as {self.role.name}"
