# Architecture Review & Production-Readiness Plan

## Current State Summary

The app is a multi-tenant SaaS scaffold with:
- **Backend**: FastAPI + SQLAlchemy 2.0 async + PostgreSQL + Alembic + JWT auth
- **Frontend**: React 19 + TypeScript + Vite + Zustand + React Query + Shadcn/ui + Tailwind 4
- **Infra**: Docker + docker-compose

Auth, RBAC (superadmin / admin / user), multi-tenancy isolation, and basic CRUD for users/tenants are already implemented. The folder layout is clean for a prototype but needs structural additions before real business logic lands.

---

## 1. Backend — What's Good

| Area | Status |
|---|---|
| Async-first (asyncpg + async SQLAlchemy) | Done |
| Pydantic v2 schemas separated from ORM models | Done |
| JWT access + refresh flow | Done |
| Tenant isolation via `tenant_filter()` | Done |
| RBAC via `require_role()` dependency | Done |
| Alembic migrations with seed data | Done |
| Config via pydantic-settings + `.env` | Done |

---

## 2. Backend — What's Missing for Production

### 2.1 Add a Service Layer (`app/services/`)

**Problem**: All business logic lives inline in route handlers. When you add real domain logic (billing, onboarding, notifications, etc.) the route files will bloat and become untestable.

**Action**: Introduce `app/services/` — one module per domain.

```
app/
  services/
    __init__.py
    auth_service.py      # login, token rotation, password reset
    user_service.py      # user CRUD + business rules
    tenant_service.py    # tenant provisioning, deactivation
```

Route handlers become thin: validate input → call service → return response. Services receive `AsyncSession` and return domain objects or raise domain exceptions.

---

### 2.2 Centralized Exception Handling (`app/core/exceptions.py`)

**Problem**: Every route manually raises `HTTPException` with inline messages. No consistent error shape. No way to add structured error codes clients can switch on.

**Action**:

1. Create domain exception classes:
   ```python
   class AppError(Exception):
       def __init__(self, code: str, message: str, status: int = 400): ...

   class NotFoundError(AppError): ...
   class ConflictError(AppError): ...
   class ForbiddenError(AppError): ...
   ```

2. Register a FastAPI exception handler in `main.py`:
   ```python
   @app.exception_handler(AppError)
   async def app_error_handler(request, exc):
       return JSONResponse(status_code=exc.status, content={"code": exc.code, "detail": exc.message})
   ```

3. Service layer raises `NotFoundError("USER_NOT_FOUND", "...")` — route handlers never touch `HTTPException`.

---

### 2.3 Logging (`app/core/logging.py`)

**Problem**: Zero logging. In production you need structured logs for debugging, auditing, and alerting.

**Action**:

- Configure Python `logging` (or `structlog` for JSON output) in a central module.
- Add a request-id middleware that tags every log line with a correlation ID.
- Log at minimum: auth events (login success/fail), CRUD mutations, unhandled exceptions.

---

### 2.4 Request Validation & Rate Limiting Middleware

**Problem**: No rate limiting on `/auth/login` (brute-force risk). No request-ID propagation.

**Action**:

- Add `slowapi` or a custom middleware for rate limiting on auth endpoints.
- Add a `X-Request-ID` middleware for tracing.

---

### 2.5 Health Check Improvements

**Problem**: `/health` returns `{"status": "ok"}` without checking the DB.

**Action**: Add a readiness probe that pings the database:

```python
@app.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ready"}
```

---

### 2.6 CORS Hardening

**Problem**: CORS allows `localhost:3000` only — needs to be configurable per environment.

**Action**: Move allowed origins to `Settings` so staging/production can set their own.

---

### 2.7 Pagination

**Problem**: `GET /admin/users` and `GET /admin/tenants` return all records — won't scale.

**Action**: Add a reusable pagination dependency:

```
app/core/pagination.py   # PaginationParams(offset, limit) + paginated response envelope
```

Apply to all list endpoints.

---

### 2.8 Tests (`tests/`)

**Problem**: No test directory exists.

**Action**:

```
backend/
  tests/
    conftest.py            # fixtures: async test client, test DB, auth helpers
    test_auth.py
    test_users.py
    test_tenants.py
```

Use `pytest` + `httpx.AsyncClient` + an in-memory or test-container PostgreSQL.

---

### 2.9 Proposed Backend Tree (After Changes)

```
backend/
  app/
    __init__.py
    main.py
    api/
      __init__.py
      auth.py
      users.py
      tenants.py
      dashboard.py
    core/
      __init__.py
      config.py
      database.py
      dependencies.py
      exceptions.py          ← NEW
      logging.py             ← NEW
      pagination.py          ← NEW
      security.py
      tenant.py
    models/
      __init__.py
      base.py
      user.py
      tenant.py
      role.py
    schemas/
      __init__.py
      auth.py
      user.py
      tenant.py
      common.py              ← NEW (PaginatedResponse, ErrorResponse)
    services/                ← NEW
      __init__.py
      auth_service.py
      user_service.py
      tenant_service.py
  tests/                     ← NEW
    conftest.py
    test_auth.py
    test_users.py
    test_tenants.py
  alembic/
  alembic.ini
  pyproject.toml
  Dockerfile
```

---

## 3. Frontend — What's Good

| Area | Status |
|---|---|
| TypeScript strict mode | Done |
| Zustand for auth state | Done |
| React Query for server-state CRUD | Done |
| Shadcn/ui component library | Done |
| Axios interceptor with silent token refresh | Done |
| Route guards (Private / Admin / SuperAdmin / Public) | Done |
| Toast notifications via Sonner | Done |
| Tailwind 4 with CSS variable theming | Done |
| Path alias `@/*` | Done |

---

## 4. Frontend — What's Missing for Production

### 4.1 Extract Shared Types (`src/types/`)

**Problem**: Interfaces (`User`, `Tenant`, `Stats`) are duplicated and defined inline inside page components. When business logic grows, you'll have conflicting type definitions.

**Action**:

```
src/
  types/
    index.ts          # re-exports
    auth.ts           # User, LoginRequest, TokenResponse
    user.ts           # UserListItem, UserCreatePayload, UserUpdatePayload
    tenant.ts         # Tenant, TenantCreatePayload, TenantUpdatePayload
    dashboard.ts      # DashboardStats
    common.ts         # PaginatedResponse<T>, ApiError
```

All pages and hooks import from `@/types`.

---

### 4.2 Extract API Calls into a Service Layer (`src/services/`)

**Problem**: Raw `api.get(...)` / `api.post(...)` calls are scattered across page components. URLs are string literals repeated in multiple files.

**Action**:

```
src/
  services/
    auth.service.ts       # login(), refreshToken(), getMe()
    user.service.ts       # getUsers(), createUser(), updateUser()
    tenant.service.ts     # getTenants(), createTenant(), updateTenant()
    dashboard.service.ts  # getStats()
```

Each service function is typed (takes payload, returns typed response). Page components call services, not raw Axios.

---

### 4.3 Extract Custom Hooks (`src/hooks/`)

**Problem**: `useQuery` / `useMutation` boilerplate is repeated in every page. Query keys are inline strings.

**Action**:

```
src/
  hooks/
    useUsers.ts           # useUsersQuery(), useCreateUser(), useUpdateUser()
    useTenants.ts         # useTenantsQuery(), useCreateTenant(), useUpdateTenant()
    useDashboard.ts       # useDashboardStats()
```

Centralized query keys prevent cache misses. Hooks encapsulate loading/error/success toast logic.

---

### 4.4 Break Down Page Components into Sub-Components

**Problem**: `UsersPage.tsx` and `TenantsPage.tsx` are monolithic (~200-300+ lines each) — they own table rendering, dialog forms, state, and CRUD logic all in one file.

**Action** — example for Users:

```
src/
  pages/
    users/
      UsersPage.tsx             # orchestrator — uses hooks, renders children
      UserTable.tsx             # table with columns, sorting
      UserCreateDialog.tsx      # create-user modal form
      UserEditDialog.tsx        # edit-user modal form
```

Same pattern for tenants, and any future domain pages.

---

### 4.5 Add an Error Boundary

**Problem**: No React error boundary exists. An unhandled JS error crashes the whole app with a white screen.

**Action**:

```
src/
  components/
    ErrorBoundary.tsx     # catches render errors, shows fallback UI
```

Wrap the root `<Routes>` in `App.tsx` with this boundary.

---

### 4.6 Loading / Skeleton Components

**Problem**: Loading states are plain text ("Loading..."). Looks unfinished.

**Action**: Add skeleton placeholders for tables and cards using Shadcn/ui's Skeleton primitive (or a simple shimmer component). Not strictly architectural — but a production expectation.

---

### 4.7 Form Handling (react-hook-form + zod)

**Problem**: Forms use raw `useState` per field. No client-side validation. As forms get more complex (business logic), this will become hard to maintain.

**Action**:

- Add `react-hook-form` + `zod` (both already common with Shadcn/ui).
- Create reusable form field wrappers that plug into Shadcn/ui inputs.
- Validate before submit on the client side with the same rules the backend enforces.

---

### 4.8 Proposed Frontend Tree (After Changes)

```
src/
  main.tsx
  App.tsx
  index.css
  types/                        ← NEW
    index.ts
    auth.ts
    user.ts
    tenant.ts
    dashboard.ts
    common.ts
  services/                     ← NEW
    auth.service.ts
    user.service.ts
    tenant.service.ts
    dashboard.service.ts
  hooks/                        ← NEW
    useUsers.ts
    useTenants.ts
    useDashboard.ts
  stores/
    auth.ts
  lib/
    api.ts
    errors.ts
    utils.ts
  components/
    Layout.tsx
    ErrorBoundary.tsx           ← NEW
    guards.tsx
    ui/                         # Shadcn/ui (unchanged)
      ...
  pages/
    LoginPage.tsx
    DashboardPage.tsx
    users/                      ← NEW (split from single file)
      UsersPage.tsx
      UserTable.tsx
      UserCreateDialog.tsx
      UserEditDialog.tsx
    tenants/                    ← NEW (split from single file)
      TenantsPage.tsx
      TenantTable.tsx
      TenantCreateDialog.tsx
      TenantEditDialog.tsx
```

---

## 5. Priority Order

Listed from highest to lowest impact for production-readiness:

| # | Change | Side | Why |
|---|--------|------|-----|
| 1 | Backend service layer | BE | Foundation — all future business logic goes here |
| 2 | Centralized exceptions | BE | Consistent error contract for the frontend |
| 3 | Frontend types extraction | FE | Prevents type drift as domain grows |
| 4 | Frontend API service layer | FE | Single source of truth for endpoints |
| 5 | Frontend custom hooks | FE | Removes duplication, centralizes cache keys |
| 6 | Logging | BE | Non-negotiable for production debugging |
| 7 | Error boundary | FE | Prevents white-screen crashes |
| 8 | Page component decomposition | FE | Maintainability as pages get complex |
| 9 | Backend pagination | BE | List endpoints won't scale without it |
| 10 | Backend tests | BE | Safety net before adding business logic |
| 11 | Form validation (zod + RHF) | FE | Better UX + client-side safety |
| 12 | Rate limiting + request-ID | BE | Security + observability |
| 13 | CORS config from env | BE | Deploy to staging/prod without code change |
| 14 | Health check with DB ping | BE | Proper k8s readiness probe |
| 15 | Skeleton loading components | FE | Polish |

---

## 6. What NOT to Change

- **Don't add a repository layer** — SQLAlchemy 2.0 `select()` is already clean. A repository would add indirection without value at this scale.
- **Don't switch state management** — Zustand for auth + React Query for server state is the right split.
- **Don't restructure `core/`** — the current `config / database / dependencies / security / tenant` split is fine.
- **Don't add i18n, feature flags, or analytics yet** — add these when the business logic demands them, not preemptively.
- **Don't over-abstract the UI** — Shadcn/ui components are already the abstraction layer. Don't wrap them in another layer.
