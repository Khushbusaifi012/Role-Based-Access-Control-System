from rest_framework import serializers

from .models import Feature, Membership, Organization, Role, RolePermission


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ("id", "code", "name", "module", "description")


class RolePermissionSerializer(serializers.ModelSerializer):
    feature_code = serializers.CharField(source="feature.code", read_only=True)
    feature_name = serializers.CharField(source="feature.name", read_only=True)

    class Meta:
        model = RolePermission
        fields = ("id", "feature", "feature_code", "feature_name", "is_enabled")


class RoleSerializer(serializers.ModelSerializer):
    permissions = RolePermissionSerializer(many=True, read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True, default="System")

    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "slug",
            "organization",
            "organization_name",
            "is_default",
            "description",
            "permissions",
        )
        read_only_fields = ("is_default",)

    def validate(self, attrs):
        if not self.instance or not self.instance.organization:
            return attrs
        slug = attrs.get("slug", self.instance.slug)
        qs = Role.objects.filter(organization=self.instance.organization, slug=slug).exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({"slug": "Role with this slug already exists in organization."})
        return attrs


class RoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("name", "slug", "description", "organization")

    def validate(self, attrs):
        org = attrs.get("organization")
        slug = attrs.get("slug")
        if Role.objects.filter(organization=org, slug=slug).exists():
            raise serializers.ValidationError("Role with this slug already exists in organization.")
        return attrs


class RolePermissionUpdateSerializer(serializers.Serializer):
    feature_code = serializers.CharField()
    is_enabled = serializers.BooleanField()


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "slug", "is_active", "created_at")


class MembershipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ("user", "organization", "role")
