from django.contrib import admin

from .models import Feature, Membership, Organization, Role, RolePermission


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "module")
    list_filter = ("module",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "organization", "is_default")
    list_filter = ("is_default", "organization")
    inlines = [RolePermissionInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "role", "is_active")
    list_filter = ("organization", "role")
