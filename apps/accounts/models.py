from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def get_org_membership(self, org_id):
        return self.memberships.filter(organization_id=org_id, is_active=True).select_related("role").first()

    def has_feature(self, org_id, feature_code):
        membership = self.get_org_membership(org_id)
        if not membership:
            return False
        return membership.role.has_feature(feature_code)
