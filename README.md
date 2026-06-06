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
- MySQL (recommended) or SQLite (fallback if `.env` is not configured)

---

## Setup Instructions

> **Note:** The `.env` file is **not** included in this repo (it contains secrets). You must create it locally after cloning.

### 1. Clone the repository

```bash
git clone <your-github-repo-url>
cd RBAC
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and edit it with your own values:

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Open `.env` and set your **MySQL password** and a **SECRET_KEY**.

#### Option A — MySQL (recommended)

1. Make sure MySQL is running on your machine.
2. Create the database (one-time):

   ```bash
   # MySQL Workbench mein scripts/create_database.sql run karo, ya:
   mysql -u root -p < scripts/create_database.sql
   ```

3. In `.env`, set:

   ```env
   DB_ENGINE=mysql
   DB_NAME=rbac_db
   DB_USER=root
   DB_PASSWORD=your_password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```

#### Option B — SQLite (quick local demo, no MySQL needed)

Either skip creating `.env`, or set in `.env`:

```env
DB_ENGINE=sqlite
```

Django will use `db.sqlite3` automatically.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Seed demo data

```bash
python manage.py seed_demo
```

This creates demo organizations, roles, features, and test users.

### 7. Start the server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## Demo Login Credentials

| Email | Password | Org | Role |
|-------|----------|-----|------|
| admin@acme.com | admin123 | Acme Corp | Admin |
| manager@acme.com | manager123 | Acme Corp | Manager |
| member@acme.com | member123 | Acme Corp | Member |
| viewer@acme.com | viewer123 | Acme Corp | Viewer |

---

## How RBAC Works

1. **Features** are system-wide capability codes (e.g. `users.manage`)
2. **Roles** bundle features — default roles are shared; custom roles are per-org
3. **Membership** links a user to an org with one role
4. Permission check: `user.has_feature(org_id, "audit.view")`

---

## Project Structure (quick reference)

| Path | Purpose |
|------|---------|
| `.env.example` | Template for local `.env` (safe to share) |
| `.env` | Your local secrets — **never commit this** |
| `scripts/create_database.sql` | Creates empty MySQL database before migrate |
| `apps/rbac/` | Roles, features, permissions logic |
| `apps/accounts/` | Users, login, dashboard |
| `apps/audit/` | Audit logging |
