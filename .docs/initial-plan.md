# Multi-Tenant SaaS Boilerplate (Python / React / Postgres)

## Architecture Overview

- **Backend:** FastAPI, SQLAlchemy 2.0 (Async), Alembic, Pydantic v2, bcrypt. **uv** for package management.
- **Frontend:** React (Vite), TypeScript, Tailwind CSS, shadcn/ui, TanStack Query + TanStack Table, Zustand. **npm** for package management.
- **Database:** PostgreSQL (Shared-schema multi-tenancy — all tenants in one DB, isolated by `tenant_id`).
- **Auth:** JWT with access + refresh tokens. Tenant ID embedded in token payload.
- **DevOps:** Docker & Docker Compose.

---

## Phase 1: Docker & Project Setup

### Monorepo Structure

```
/
├── backend/           # FastAPI app
│   ├── app/
│   │   ├── api/       # Route modules
│   │   ├── core/      # Config, security, dependencies
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   └── main.py
│   ├── alembic/
│   ├── pyproject.toml   # uv project config
│   ├── uv.lock          # uv lockfile
│   └── Dockerfile
├── frontend/          # React app
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .env
```

### Docker Compose Services

| Service    | Image / Base       | Exposed Port |
|------------|--------------------|--------------|
| `db`       | Postgres 18        | 5432         |
| `backend`  | Python 3.14        | 8000         |
| `frontend` | Node 24 LTS        | 3000         |

### Environment Variables (`.env`)

```
POSTGRES_USER=saas
POSTGRES_PASSWORD=<generate>
POSTGRES_DB=saas_db
DATABASE_URL=postgresql+asyncpg://saas:<pw>@db:5432/saas_db

JWT_SECRET=<generate>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Deliverables

- `docker-compose up` boots all three services and the DB is reachable from the backend.
- FastAPI responds on `http://localhost:8000/health`.
- React dev server responds on `http://localhost:3000`.

---

## Phase 2: Database Schema & Migrations (SQLAlchemy Async + Alembic)

### Tables

**tenants**
| Column       | Type        | Notes                      |
|-------------|-------------|----------------------------|
| id          | UUID (PK)   | Default `uuid4`            |
| name        | VARCHAR     | Display name               |
| slug        | VARCHAR     | Unique, URL-safe           |
| is_active   | BOOLEAN     | Default `true`             |
| created_at  | TIMESTAMP   | Server default `now()`     |

**roles**
| Column      | Type        | Notes                               |
|-------------|-------------|---------------------------------------|
| id          | INT (PK)    | Auto-increment                       |
| name        | VARCHAR     | e.g. `superadmin`, `admin`, `user`   |

> Keep roles simple — just a name string. Permissions/JSONB can be added later when real permission logic is needed. Avoid over-engineering.

**users**
| Column          | Type        | Notes                           |
|-----------------|-------------|---------------------------------|
| id              | UUID (PK)   | Default `uuid4`                 |
| email           | VARCHAR     | Unique                          |
| hashed_password | VARCHAR     |                                 |
| is_active       | BOOLEAN     | Default `true`                  |
| tenant_id       | UUID (FK)   | → `tenants.id`, indexed         |
| role_id         | INT (FK)    | → `roles.id`                    |
| created_at      | TIMESTAMP   | Server default `now()`          |

### Seed Data (initial migration or startup script)

1. Create a **"system" tenant** (`slug: system`). This is the SuperAdmin tenant.
2. Create three **roles**: `superadmin`, `admin`, `user`.
3. Create a **default SuperAdmin user** in the system tenant (`admin@system.local` / changeable password).

### Alembic Setup

- Configure `env.py` for async engine (`asyncpg`).
- All future entity tables must include a `tenant_id` FK column with an index.

### Deliverables

- `alembic upgrade head` creates all tables and seeds the initial data.
- The SuperAdmin can log in immediately after first boot.

---

## Phase 3: Auth & Tenant Resolution

### Password Hashing

- Use `bcrypt` directly for hashing and verifying passwords (`passlib` is unmaintained and incompatible with recent `bcrypt` versions).

### JWT Token Strategy

**Access Token** (short-lived, ~15 min):
- Payload: `{ sub: user_id, tid: tenant_id, role: role_name, type: "access" }`

**Refresh Token** (long-lived, ~7 days):
- Payload: `{ sub: user_id, type: "refresh" }`
- Stored as HttpOnly cookie or returned in response body (frontend stores in memory/Zustand).

### FastAPI Dependencies

1. **`get_db()`** — yields an async SQLAlchemy session.
2. **`get_current_user(token)`** — decodes access token, loads User with Tenant and Role eagerly loaded. Rejects expired/invalid tokens.
3. **`require_role(role_name)`** — dependency factory that checks the user's role. Usage: `Depends(require_role("admin"))`.
4. **`tenant_filter(query, user)`** — helper that appends `.where(Model.tenant_id == user.tenant_id)` to any query. SuperAdmin users (system tenant) bypass the filter and can query across all tenants.

### CORS

- Configure `CORSMiddleware` to allow the frontend origin (`http://localhost:3000`).

### Deliverables

- Auth dependencies are unit-testable.
- A protected test endpoint confirms tenant isolation works.

---

## Phase 4: Backend API Endpoints

### Auth (`/api/auth`)

| Method | Path            | Auth     | Description                                    |
|--------|-----------------|----------|------------------------------------------------|
| POST   | `/auth/login`   | Public   | Email + password → access token + refresh token |
| POST   | `/auth/refresh` | Refresh  | Refresh token → new access token                |
| GET    | `/auth/me`      | Bearer   | Returns current user profile with tenant & role |

> No public registration. Tenants and users are created by SuperAdmin only.

### SuperAdmin — Tenant Management (`/api/admin/tenants`)

| Method | Path                    | Role        | Description               |
|--------|-------------------------|-------------|---------------------------|
| GET    | `/admin/tenants`        | superadmin  | List all tenants           |
| POST   | `/admin/tenants`        | superadmin  | Create a new tenant        |
| PATCH  | `/admin/tenants/{id}`   | superadmin  | Update tenant (name, active) |
| DELETE | `/admin/tenants/{id}`   | superadmin  | Deactivate a tenant        |

### Tenant Admin — User Management (`/api/admin/users`)

| Method | Path                   | Role          | Description                              |
|--------|------------------------|---------------|------------------------------------------|
| GET    | `/admin/users`         | admin         | List users in current tenant              |
| POST   | `/admin/users`         | admin         | Create user in current tenant             |
| PATCH  | `/admin/users/{id}`    | admin         | Update user (role, active status)         |
| DELETE | `/admin/users/{id}`    | admin         | Deactivate user                           |

> SuperAdmin can also access these endpoints and manage users across any tenant.

### Dashboard (`/api/dashboard`)

| Method | Path               | Auth   | Description                              |
|--------|--------------------|--------|------------------------------------------|
| GET    | `/dashboard/stats`  | Bearer | Returns dummy metrics scoped to tenant   |

Dummy stats example: `{ total_users, active_users, revenue: random, growth: random }`.

### Deliverables

- All endpoints work via Swagger UI (`/docs`).
- Tenant isolation is enforced — a tenant admin cannot see another tenant's users.

---

## Phase 5: Frontend Foundation

### Tooling Setup

- Vite + React + TypeScript.
- Tailwind CSS + shadcn/ui initialized.
- TanStack Query for server state.
- Zustand for auth state (`user`, `accessToken`, `isAuthenticated`).

### Auth Flow (Zustand + Axios)

1. On login, store access token in Zustand (memory). Store refresh token in memory or HttpOnly cookie.
2. Axios request interceptor attaches `Authorization: Bearer <accessToken>` to every request.
3. Axios response interceptor catches `401`, attempts a silent refresh via `/auth/refresh`, retries the original request. If refresh fails, log out.

### Routing (React Router)

- **Public routes:** `/login`
- **Private routes (auth required):** `/dashboard`, `/settings`
- **Admin routes (admin/superadmin):** `/admin/users`
- **SuperAdmin routes:** `/admin/tenants`
- All private routes wrapped in a `<Layout>` with sidebar + topbar.
- Route guards redirect to `/login` if not authenticated.

### Deliverables

- Login page works end-to-end with the backend.
- Token refresh works silently.
- Unauthorized users are redirected to login.

---

## Phase 6: UI Implementation

### Layout & Sidebar

- Modern minimalist sidebar using shadcn/ui components.
- Sidebar links:
  - **Dashboard** — visible to all authenticated users.
  - **Admin > Users** — visible to `admin` and `superadmin` only.
  - **Admin > Tenants** — visible to `superadmin` only.
- Topbar: shows current user email, tenant name, and a logout button.

### Pages

**Login Page:**
- Clean centered card with email/password form.
- Error display for invalid credentials.

**Dashboard Page:**
- Grid of metric cards (shadcn/ui `Card` component) showing dummy stats from `/dashboard/stats`.
- Minimalist, card-based layout.

**User Management Page (Admin):**
- TanStack Table listing users in the current tenant.
- Columns: email, role, active status, created date.
- Actions: change role, toggle active status.
- "Create User" button opens a dialog/form.

**Tenant Management Page (SuperAdmin):**
- TanStack Table listing all tenants.
- Columns: name, slug, active status, created date.
- Actions: edit, deactivate.
- "Create Tenant" button opens a dialog/form.
- Ability to create the first admin user for a new tenant.

### Deliverables

- All pages are functional and connected to the API.
- Role-based visibility works correctly in the sidebar and via route guards.
- UI is clean, responsive, and uses a consistent design system.
