from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.accounts.models import User
from apps.rbac.models import Feature, Membership, Organization, Role, RolePermission

DEFAULT_FEATURES = [
    ("users.view", "View Users", "users"),
    ("users.manage", "Manage Users", "users"),
    ("roles.view", "View Roles", "roles"),
    ("roles.manage", "Manage Roles", "roles"),
    ("org.manage", "Manage Organization", "org"),
    ("audit.view", "View Audit Logs", "audit"),
    ("reports.view", "View Reports", "reports"),
    ("reports.export", "Export Reports", "reports"),
]

DEFAULT_ROLES = {
    "admin": {
        "name": "Admin",
        "description": "Full access within organization",
        "features": ["users.view", "users.manage", "roles.view", "roles.manage", "org.manage", "audit.view", "reports.view", "reports.export"],
    },
    "manager": {
        "name": "Manager",
        "description": "Manage users and view reports",
        "features": ["users.view", "users.manage", "roles.view", "audit.view", "reports.view", "reports.export"],
    },
    "member": {
        "name": "Member",
        "description": "Basic access",
        "features": ["users.view", "reports.view"],
    },
    "viewer": {
        "name": "Viewer",
        "description": "Read-only access",
        "features": ["users.view", "reports.view"],
    },
}


class Command(BaseCommand):
    help = "Seed demo data for Dynamic RBAC system"

    def handle(self, *args, **options):
        self.stdout.write("Creating features...")
        feature_map = {}
        for code, name, module in DEFAULT_FEATURES:
            feature, _ = Feature.objects.get_or_create(
                code=code,
                defaults={"name": name, "module": module},
            )
            feature_map[code] = feature

        self.stdout.write("Creating default roles...")
        role_map = {}
        for slug, config in DEFAULT_ROLES.items():
            role, created = Role.objects.get_or_create(
                slug=slug,
                organization=None,
                defaults={
                    "name": config["name"],
                    "description": config["description"],
                    "is_default": True,
                },
            )
            if created:
                for code, feature in feature_map.items():
                    RolePermission.objects.create(
                        role=role,
                        feature=feature,
                        is_enabled=code in config["features"],
                    )
            role_map[slug] = role

        orgs_data = [
            ("Acme Corp", "acme"),
        ]
        org_map = {}
        for name, slug in orgs_data:
            org, _ = Organization.objects.get_or_create(slug=slug, defaults={"name": name})
            org_map[slug] = org

        # Remove old demo org if it exists from previous seeds
        Organization.objects.filter(slug="globex").delete()
        User.objects.filter(email__endswith="@globex.com").delete()

        users_data = [
            ("admin@acme.com", "admin123", "acme", "admin"),
            ("manager@acme.com", "manager123", "acme", "manager"),
            ("member@acme.com", "member123", "acme", "member"),
            ("viewer@acme.com", "viewer123", "acme", "viewer"),
        ]
        for email, password, org_slug, role_slug in users_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": email.replace("@", "_")},
            )
            user.set_password(password)
            user.is_active = True
            user.save()
            Membership.objects.get_or_create(
                user=user,
                organization=org_map[org_slug],
                defaults={"role": role_map[role_slug]},
            )

        # Custom role example for Acme
        custom_role, created = Role.objects.get_or_create(
            slug="sales-lead",
            organization=org_map["acme"],
            defaults={
                "name": "Sales Lead",
                "description": "Custom role with report export only",
                "is_default": False,
            },
        )
        if created:
            for code, feature in feature_map.items():
                RolePermission.objects.create(
                    role=custom_role,
                    feature=feature,
                    is_enabled=code in ["users.view", "reports.view", "reports.export"],
                )

        self.stdout.write(self.style.SUCCESS("Seed data created successfully!"))
        self.stdout.write("\nDemo accounts:")
        for email, password, org_slug, role_slug in users_data:
            self.stdout.write(f"  {email} / {password}  ->  {org_slug} ({role_slug})")
