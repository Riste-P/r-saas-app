# Multi-Tenant SaaS Application

A full-stack multi-tenant SaaS application with role-based access control, built with FastAPI, React, and PostgreSQL.

## Tech Stack

**Backend:** Python 3.14+ / FastAPI / SQLAlchemy (async) / Alembic / JWT Auth

**Frontend:** React 19 / TypeScript / Vite / Tailwind CSS / Radix UI / Zustand / React Query

**Database:** PostgreSQL 18

**Infrastructure:** Docker / Docker Compose

## Features

- **Multi-Tenancy** -- Tenant isolation with per-tenant user management
- **Role-Based Access Control** -- Three roles: `superadmin`, `admin`, `user`
- **JWT Authentication** -- Access + refresh token flow with automatic silent refresh
- **User Management** -- CRUD operations scoped by tenant and role
- **Tenant Management** -- Create and manage tenants (superadmin only)
- **Dashboard** -- Role-aware dashboard view
- **Soft Deletes** -- Deactivation instead of hard deletion

## Project Structure

```
r-saas-app/
├── backend/
│   ├── app/
│   │   ├── api/            # Route handlers (auth, users, tenants, dashboard)
│   │   ├── core/           # Config, database, security, dependencies
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   └── services/       # Business logic layer
│   ├── alembic/            # Database migrations
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── pages/          # Login, Dashboard, Users, Tenants
│   │   ├── components/     # Layout, route guards, UI primitives
│   │   ├── services/       # API service layer (axios)
│   │   ├── stores/         # Zustand auth store
│   │   ├── hooks/          # Custom React hooks
│   │   └── types/          # TypeScript type definitions
├── docker-compose.yml
└── .env
```

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd r-saas-app
   ```

2. **Configure environment variables**

   Copy or edit the `.env` file in the project root. The defaults work for local development:
   ```env
   POSTGRES_USER=saas
   POSTGRES_PASSWORD=saas_dev_password_2026
   POSTGRES_DB=saas_db
   DATABASE_URL=postgresql+asyncpg://saas:saas_dev_password_2026@db:5432/saas_db

   JWT_SECRET=dev-secret-change-in-production-k8x92mf
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

   > **Warning:** Change `JWT_SECRET` and `POSTGRES_PASSWORD` before deploying to production.

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**

   | Service  | URL                     |
   |----------|-------------------------|
   | Frontend | http://localhost:3000    |
   | Backend  | http://localhost:8000    |
   | API Docs | http://localhost:8000/docs |

5. **Default credentials**
   ```
   Email:    admin@system.com
   Password: changeme
   ```

### Local Development (without Docker)

**Backend:**
```bash
cd backend
uv sync
alembic upgrade head
uv run uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Authentication
| Method | Endpoint             | Description          |
|--------|----------------------|----------------------|
| POST   | `/api/auth/login`    | Login                |
| POST   | `/api/auth/refresh`  | Refresh access token |
| GET    | `/api/auth/me`       | Get current user     |

### Users (admin / superadmin)
| Method | Endpoint                    | Description     |
|--------|-----------------------------|-----------------|
| GET    | `/api/admin/users`          | List users      |
| POST   | `/api/admin/users`          | Create user     |
| PATCH  | `/api/admin/users/{id}`     | Update user     |
| DELETE | `/api/admin/users/{id}`     | Deactivate user |

### Tenants (superadmin only)
| Method | Endpoint                      | Description       |
|--------|-------------------------------|-------------------|
| GET    | `/api/admin/tenants`          | List tenants      |
| POST   | `/api/admin/tenants`          | Create tenant     |
| PATCH  | `/api/admin/tenants/{id}`     | Update tenant     |
| DELETE | `/api/admin/tenants/{id}`     | Deactivate tenant |

### Dashboard
| Method | Endpoint          | Description    |
|--------|-------------------|----------------|
| GET    | `/api/dashboard`  | Dashboard data |

## Roles & Permissions

| Role       | Scope                                          |
|------------|-------------------------------------------------|
| superadmin | Full system access -- manage all tenants & users |
| admin      | Manage users within their own tenant             |
| user       | Dashboard access only                            |

## License

This project is provided as-is for development purposes.
