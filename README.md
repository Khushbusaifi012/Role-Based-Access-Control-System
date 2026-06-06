# Dynamic RBAC System

A simple **Dynamic Role-Based Access Control (RBAC)** system with multi-organization support, feature toggles (on/off), default + custom roles, and basic audit logging.

## Features

- **Multi-organization** — Users belong to orgs with separate roles per org
- **Default roles** — Admin, Manager, Member, Viewer (system-wide templates)
- **Custom roles** — Create org-specific roles with granular feature controls
- **Feature flags** — Toggle permissions ON/OFF per role (users.manage, audit.view, etc.)
- **Audit logs** — Login, logout, role creation, permission changes
- **REST API** — Django REST Framework endpoints
- **Simple UI** — Django templates (no Next.js needed for demo)

## Tech Stack

- Python 3.10+
- Django 4.2 + Django REST Framework
- MySQL (recommended) or SQLite (default if `.env` not set)

### Dependencies + migrations

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Seed demo data
python manage.py seed_demo

# 4. Start server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** and login with:

| Email | Password | Org | Role |
|-------|----------|-----|------|
| admin@acme.com | admin123 | Acme Corp | Admin |
| manager@acme.com | manager123 | Acme Corp | Manager |
| member@acme.com | member123 | Acme Corp | Member |
| viewer@acme.com | viewer123 | Acme Corp | Viewer |


## How RBAC Works

1. **Features** are system-wide capability codes (e.g. `users.manage`)
2. **Roles** bundle features — default roles are shared; custom roles are per-org
3. **Membership** links a user to an org with one role
4. Permission check: `user.has_feature(org_id, "audit.view")`
