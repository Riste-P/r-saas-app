# CLAUDE.md

## Project Overview

Multi-tenant SaaS app. Backend is FastAPI + SQLAlchemy (async) + PostgreSQL. Frontend is React 19 + Vite + TypeScript.

## Running the App

```bash
docker-compose up --build          # Start everything (DB, backend :8000, frontend :3000)
docker-compose --profile test up test --build   # Run backend tests
```

## Backend

**Structure:** `backend/app/`
- `api/` — Route handlers (endpoints)
- `services/` — Business logic
- `database/` — Models, migrations, session, base mixins (`database/models/`, `database/migrations/`)
- `dto/` — Pydantic request/response DTOs
- `core/` — Config, dependencies (auth/roles), exceptions, pagination
- `utils/` — Stateless helpers (JWT, hashing, logging)

**Rules:**
- All new DB-related code (models, migrations, queries) goes in `app/database/`
- Endpoints receive and return DTOs only. Map domain entities to DTOs via `ResponseDTO.from_entity(entity)`
- Business logic goes in services. Endpoints orchestrate service calls
- Services accept DTO objects as parameters for create/update operations
- Soft delete via `deleted_at` timestamp — always filter with `.where(Model.deleted_at.is_(None))`
- Multi-tenant isolation via `tenant_filter()` from `database/utils/common.py`
- Custom exceptions (`NotFoundError`, `ConflictError`, `ForbiddenError`) from `core/exceptions.py` — raise from services, never catch in endpoints
- Run tests when completing a feature or when asked — not after every small change
- Do not add tests unless explicitly asked

## Frontend

**Structure:** `frontend/src/`
- `pages/` — Page components (organized by feature in subfolders)
- `components/` — Shared components (`components/ui/` has shadcn/ui primitives)
- `hooks/` — TanStack Query hooks per feature (useUsers, useTenants, etc.)
- `services/` — API call functions (axios-based, one file per feature)
- `stores/` — Zustand stores (auth)
- `types/` — TypeScript type definitions
- `lib/` — Utilities (axios instance, zod schemas, error helpers)

**Rules:**
- Use existing libraries for building components: shadcn/ui, Radix UI, Tailwind CSS, Lucide icons. Ask before adding new libraries
- Forms use Zod schemas (`lib/schemas.ts`) + React Hook Form + `@hookform/resolvers/zod`
- Data fetching via TanStack Query hooks in `hooks/`. Actual fetch logic in `services/`
- Keep components small — split when a component grows large, but don't split preemptively
- Use Chrome MCP DevTools and the running Docker app (localhost:3000) to test UI changes when needed
