from rest_framework.permissions import BasePermission


class HasOrgFeature(BasePermission):
    """Check if user has a specific feature enabled in the given organization."""

    feature_code = None

    def has_permission(self, request, view):
        org_id = request.query_params.get("org_id") or request.data.get("org_id")
        if not org_id or not request.user.is_authenticated:
            return False
        return request.user.has_feature(org_id, self.feature_code)


class CanManageRoles(HasOrgFeature):
    feature_code = "roles.manage"


class CanManageUsers(HasOrgFeature):
    feature_code = "users.manage"


class CanViewAudit(HasOrgFeature):
    feature_code = "audit.view"


class CanManageOrg(HasOrgFeature):
    feature_code = "org.manage"
