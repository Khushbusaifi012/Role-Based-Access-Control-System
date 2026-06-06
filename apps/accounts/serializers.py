from rest_framework import serializers

from apps.rbac.models import Membership

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "is_active")


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = Membership
        fields = ("id", "user", "user_email", "role", "role_name", "is_active", "joined_at")
