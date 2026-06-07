from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.serializers import MembershipSerializer, UserSerializer
from apps.audit.utils import log_audit

from .models import Feature, Membership, Organization, Role, RolePermission
from .permissions import CanManageOrg, CanManageRoles, CanManageUsers, CanViewAudit
from .serializers import (
    FeatureSerializer,
    MembershipCreateSerializer,
    OrganizationSerializer,
    RoleCreateSerializer,
    RolePermissionUpdateSerializer,
    RoleSerializer,
)


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True,
        ).distinct()


class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org_id = self.request.query_params.get("org_id")
        if not org_id:
            return Role.objects.none()
        return Role.objects.filter(
            Q(organization_id=org_id) | Q(organization__isnull=True, is_default=True)
        ).distinct()

    def get_serializer_class(self):
        if self.action == "create":
            return RoleCreateSerializer
        return RoleSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "set_permissions"):
            return [IsAuthenticated(), CanManageRoles()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        org_id = self.request.data.get("org_id")
        org = Organization.objects.get(id=org_id)
        role = serializer.save(organization=org, is_default=False)
        for feature in Feature.objects.all():
            RolePermission.objects.create(role=role, feature=feature, is_enabled=False)
        log_audit(
            self.request,
            action="CREATE",
            resource_type="Role",
            resource_id=role.id,
            organization=org,
            details={"name": role.name},
        )

    def perform_update(self, serializer):
        role = serializer.instance
        if role.is_default and role.organization is None:
            raise ValidationError("Cannot edit default roles")
        role = serializer.save()
        log_audit(
            self.request,
            action="UPDATE",
            resource_type="Role",
            resource_id=role.id,
            organization=role.organization,
            details={"name": role.name, "slug": role.slug},
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_default and instance.organization is None:
            return Response({"error": "Cannot delete default roles"}, status=status.HTTP_400_BAD_REQUEST)
        if instance.memberships.exists():
            return Response(
                {"error": "Cannot delete this role while users are assigned. Change their role first."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        log_audit(
            request,
            action="DELETE",
            resource_type="Role",
            resource_id=instance.id,
            organization=instance.organization,
            details={"name": instance.name},
        )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="permissions")
    def set_permissions(self, request, pk=None):
        role = self.get_object()
        if role.is_default and role.organization is None:
            return Response({"error": "Cannot modify system default role permissions"}, status=400)
        serializer = RolePermissionUpdateSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        for item in serializer.validated_data:
            perm, _ = RolePermission.objects.get_or_create(
                role=role,
                feature=Feature.objects.get(code=item["feature_code"]),
            )
            perm.is_enabled = item["is_enabled"]
            perm.save()
        log_audit(
            request,
            action="PERMISSION_CHANGE",
            resource_type="Role",
            resource_id=role.id,
            organization=role.organization,
            details={"permissions": serializer.validated_data},
        )
        return Response(RoleSerializer(role).data)


class FeatureListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(FeatureSerializer(Feature.objects.all(), many=True).data)


class MembershipViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, CanManageUsers]
    serializer_class = MembershipSerializer

    def get_queryset(self):
        org_id = self.request.query_params.get("org_id")
        if not org_id:
            return Membership.objects.none()
        return Membership.objects.filter(organization_id=org_id).select_related("user", "role")

    def get_serializer_class(self):
        if self.action == "create":
            return MembershipCreateSerializer
        return MembershipSerializer

    def perform_create(self, serializer):
        membership = serializer.save()
        log_audit(
            self.request,
            action="CREATE",
            resource_type="Membership",
            resource_id=membership.id,
            organization=membership.organization,
            details={"user": membership.user.email, "role": membership.role.name},
        )

    def perform_update(self, serializer):
        membership = serializer.save()
        log_audit(
            self.request,
            action="UPDATE",
            resource_type="Membership",
            resource_id=membership.id,
            organization=membership.organization,
            details={"user": membership.user.email, "role": membership.role.name},
        )


class OrgUserListView(APIView):
    permission_classes = [IsAuthenticated, CanManageUsers]

    def get(self, request):
        org_id = request.query_params.get("org_id")
        users = User.objects.filter(memberships__organization_id=org_id).distinct()
        return Response(UserSerializer(users, many=True).data)
