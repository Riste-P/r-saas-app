# Implementation Plan: Service Types, Clients & Properties, Billing & Payments

## Context

The cleaning business management app currently has auth, users, tenants, and a mock dashboard. We need to add the three core domain features: **Service Types** (what cleaning services are offered), **Clients & Properties** (who we clean for and where), and **Billing & Payments** (invoicing and payment tracking). These are implemented in dependency order since billing references both properties and service types.

**Scope decisions:**
- PDF invoice generation deferred to a later phase
- Overdue reminders = visual flagging only (auto-mark status + red badge), no email
- Sidebar stays flat (no grouping)
- Payments get their own dedicated page

---

## Phase 1: Service Types (Backend) ✅

### 1.1 Models

**Created** `backend/app/database/models/service_type.py`
```
ServiceType(Base, AuditMixin, TenantMixin):
  id: UUID (PK)
  name: String(255)
  description: String(1000), nullable
  base_price: Numeric(10,2)
  estimated_duration_minutes: Integer
  is_active: Boolean, default True
  → checklist_items: relationship, ordered by sort_order
```

**Created** `backend/app/database/models/checklist_item.py`
```
ChecklistItem(Base, AuditMixin, TenantMixin):
  id: UUID (PK)
  service_type_id: UUID FK → service_types.id, indexed
  name: String(255)
  description: String(500), nullable
  sort_order: Integer, default 0
  → service_type: relationship
```

**Modified** `backend/app/database/models/__init__.py` — added imports + `__all__`

### 1.2 Migration

- Created `service_types` and `checklist_items` tables
- Unique partial index on `(tenant_id, name) WHERE deleted_at IS NULL` for service_types

### 1.3 DTOs

**Created** `backend/app/dto/service_type.py`
- `ChecklistItemRequest(name, description?, sort_order=0)`
- `CreateServiceTypeRequest(name, description?, base_price, estimated_duration_minutes, checklist_items=[])`
- `UpdateServiceTypeRequest(name?, description?, base_price?, estimated_duration_minutes?, is_active?)`
- `UpdateChecklistRequest(items: list[ChecklistItemRequest])` — full replacement
- `ChecklistItemResponse` with `from_entity()`
- `ServiceTypeResponse` with nested `checklist_items` and `from_entity()`

### 1.4 Service

**Created** `backend/app/services/service_type_service.py`
- `list_service_types(current_user, db, offset, limit)` — tenant_filter, eager load checklist_items
- `get_service_type(id, current_user, db)` — single fetch with tenant filter
- `create_service_type(body, current_user, db)` — check name uniqueness within tenant, create with checklist items
- `update_service_type(id, body, current_user, db)` — partial update
- `update_checklist(id, body, current_user, db)` — soft-delete existing items, insert new ones
- `delete_service_type(id, current_user, db)` — soft delete

### 1.5 API Router

**Created** `backend/app/api/service_types.py` — prefix `/service-types`
| Method | Path | Role | Description |
|--------|------|------|-------------|
| GET | `/service-types` | any auth | List all |
| GET | `/service-types/{id}` | any auth | Get single |
| POST | `/service-types` | admin+ | Create |
| PATCH | `/service-types/{id}` | admin+ | Update |
| PUT | `/service-types/{id}/checklist` | admin+ | Replace checklist |
| DELETE | `/service-types/{id}` | admin+ | Soft delete |

**Modified** `backend/app/main.py` — registered router

---

## Phase 2: Service Types (Frontend) ✅

### 2.1 Types, Service, Hooks

**Created** `frontend/src/types/serviceType.ts` — ServiceType, ChecklistItem, payloads
**Modified** `frontend/src/types/index.ts` — added re-exports
**Created** `frontend/src/services/serviceType.service.ts` — CRUD + updateChecklist
**Created** `frontend/src/hooks/useServiceTypes.ts` — list key `["service-types"]`, detail key `["service-type"]`, all CRUD hooks. Uses `skipToken` for conditional detail query.

### 2.2 Schemas

**Modified** `frontend/src/lib/schemas.ts` — added `createServiceTypeSchema`, `editServiceTypeSchema`, `checklistItemSchema`

### 2.3 Pages

**Created** `frontend/src/pages/service-types/ServiceTypesPage.tsx` — DataTable with columns: Name, Base Price, Duration, Status badge, Actions
**Created** `frontend/src/pages/service-types/ServiceTypeColumns.tsx`
**Created** `frontend/src/pages/service-types/CreateServiceTypeDialog.tsx`
**Created** `frontend/src/pages/service-types/EditServiceTypeDialog.tsx`
**Created** `frontend/src/pages/service-types/DeleteServiceTypeDialog.tsx`
**Created** `frontend/src/pages/service-types/ChecklistEditor.tsx` — dialog to manage checklist items (add/remove/reorder)

### 2.4 Routing

**Modified** `frontend/src/App.tsx` — added `/service-types` route (PrivateRoute)
**Modified** `frontend/src/components/Layout.tsx` — added nav item with `ClipboardList` icon, visible to all roles

---

## Phase 3: Clients & Properties (Backend) ✅

### 3.1 Models

**Created** `backend/app/database/models/client.py`
```
Client(Base, AuditMixin, TenantMixin):
  id: UUID (PK)
  name: String(255)
  email: String(255), nullable
  phone: String(50), nullable
  address: String(500), nullable
  billing_address: String(500), nullable
  notes: Text, nullable
  is_active: Boolean, default True
  → properties: relationship
```

**Created** `backend/app/database/models/property.py`
```
PropertyType(str, Enum): house, apartment, building, commercial

Property(Base, AuditMixin, TenantMixin):
  id: UUID (PK)
  client_id: UUID FK → clients.id, nullable, indexed  (property doesn't have to belong to a client)
  parent_property_id: UUID FK → properties.id, nullable, indexed  (self-ref: apartment can be part of any non-apartment property)
  property_type: Enum(PropertyType)
  name: String(255)
  address: String(500), nullable
  city: String(100), nullable
  notes: Text, nullable
  is_active: Boolean, default True
  → client: relationship (optional)
  → parent_property: relationship (self-ref)
  → child_properties: relationship (self-ref)
```

**Constraints:**
- `client_id` is optional — properties can exist without a client and be linked later
- `parent_property_id` — apartments can be linked to any property type except other apartments (validated in service layer)
- `address` is optional

**Modified** `backend/app/database/models/__init__.py`

### 3.2 Migration

Created migration for `clients` and `properties` tables

### 3.3 DTOs

**Created** `backend/app/dto/client.py`
- `CreateClientRequest`, `UpdateClientRequest`, `ClientResponse` (includes `property_count`)

**Created** `backend/app/dto/property.py`
- `CreatePropertyRequest(client_id?, parent_property_id?, property_type, name, address?, city?, notes?, number_of_apartments?)` — `number_of_apartments` triggers auto-creation of N apartments when type=building
- `UpdatePropertyRequest(client_id?, parent_property_id?, property_type?, name?, address?, city?, notes?, is_active?)`
- `PropertySummaryResponse` — lightweight for child property listings, includes `client_name` and `is_active`
- `PropertyResponse` — full details with `child_properties: list[PropertySummaryResponse]`, `client_name`, and `parent_property_name`

### 3.4 Services

**Created** `backend/app/services/client_service.py`
- Standard CRUD with tenant_filter
- `list_clients` includes property_count subquery
- `delete_client` also soft-deletes all associated properties

**Created** `backend/app/services/property_service.py`
- `list_properties(... client_id?, property_type?, parent_property_id?, parents_only?)` — filterable, eager loads client + parent_property + child_properties. `parents_only=true` returns only properties with no parent.
- `get_property` — single fetch with tenant filter, eager loads all relationships
- `create_property` — validates client belongs to tenant (if provided); validates parent exists and is not an apartment (if provided). When `number_of_apartments` is set and type=building, atomically creates N apartment child properties (named "Apartment 1", "Apartment 2", etc.) inheriting address, city, and client_id from the building.
- `update_property` — partial update, uses `model_fields_set` to distinguish "field not sent" from "field sent as null" for `client_id` and `parent_property_id` (allows unlinking)
- `delete_property` — also soft-deletes child properties (apartments in a building)

### 3.5 API Routers

**Created** `backend/app/api/clients.py` — prefix `/clients`, standard CRUD (any auth for read, admin+ for write)
**Created** `backend/app/api/properties.py` — prefix `/properties`, CRUD + query param filters

**Modified** `backend/app/main.py` — registered both routers

---

## Phase 4: Clients & Properties (Frontend) ✅

### 4.1 Types, Services, Hooks

**Created** `frontend/src/types/client.ts`, `frontend/src/types/property.ts`
- `PropertySummary` includes `client_name: string | null` and `is_active: boolean`
- `PropertyCreatePayload` includes `number_of_apartments?: number`
- `PropertyUpdatePayload` has `client_id?: string | null` and `parent_property_id?: string | null` (allows sending explicit null to unlink)

**Modified** `frontend/src/types/index.ts`
**Created** `frontend/src/services/client.service.ts`, `frontend/src/services/property.service.ts`
**Created** `frontend/src/hooks/useClients.ts` (list key: `["clients"]`, detail key: `["client"]`), `frontend/src/hooks/useProperties.ts` (list key: `["properties"]`, detail key: `["property"]`)

**TanStack Query patterns established:**
- Detail queries use separate key namespace from list queries to prevent `invalidateQueries` conflicts with `skipToken`
- Detail queries use `skipToken` (not `enabled: !!id`) for conditional fetching
- Mutations invalidate both list and detail keys on update; only list key on delete

### 4.2 Schemas

**Modified** `frontend/src/lib/schemas.ts` — added client/property schemas
- `createPropertySchema` — default type is `"building"`, includes `number_of_apartments` (optional int 1-100)
- `editPropertySchema` — includes `is_active: boolean`

### 4.3 Pages — Clients

**Created** `frontend/src/pages/clients/ClientsPage.tsx` — columns: Name, Email, Phone, Properties (count badge), Status, Actions
**Created** `frontend/src/pages/clients/ClientColumns.tsx`
**Created** `frontend/src/pages/clients/CreateClientDialog.tsx`
**Created** `frontend/src/pages/clients/EditClientDialog.tsx`
**Created** `frontend/src/pages/clients/DeleteClientDialog.tsx`

### 4.4 Pages — Properties

**Created** `frontend/src/pages/properties/PropertiesPage.tsx`
- Columns: Expand chevron, Name, Type badge, Client, Address, Status badge, Actions
- Always fetches with `parents_only: true` — child apartments shown as expandable sub-rows
- Filter dropdowns for property type and client
- Uses TanStack Table `getExpandedRowModel` with `getRowCanExpand` based on `child_properties.length`
- `renderExpandedRows` renders child properties as actual `<TableRow>` elements (not colSpan) for column alignment, with indented name, type badge, client name, address, status badge, and Edit/Delete action dropdown
- Uses `<Fragment key={row.id}>` in DataTable for expandable row support

**Created** `frontend/src/pages/properties/PropertyColumns.tsx`
- First column is expand/collapse chevron button (ChevronRight with rotate-90 transition)
- Callbacks pass IDs (not full objects): `onEdit: (id: string) => void`

**Created** `frontend/src/pages/properties/CreatePropertyDialog.tsx`
- Default type is "building" (not "house")
- When type=building: shows number input for apartment count + info message that apartments will be auto-created
- When type=apartment: shows "Part of" dropdown (half-width grid) + info message
- Uses `useWatch` for conditional rendering based on property type (avoids Radix `flushSync` issues with `form.watch`)

**Created** `frontend/src/pages/properties/EditPropertyDialog.tsx`
- Accepts `propertyId: string | null` and uses `usePropertyQuery(propertyId)` internally (not a full Property object)
- Uses `useWatch` for `property_type` conditional rendering
- All field values use `?? ""` / `?? "none"` / `?? true` fallbacks to prevent uncontrolled→controlled warnings during Radix Select's `flushSync` re-renders
- "Part of" dropdown shown only for apartments, in half-width grid with info message
- `is_active` switch in single-column grid
- On submit: `parent_property_id` is set to null when type is not "apartment" (prevents orphaned parent links when changing type)
- Sends explicit `null` (not `undefined`) for `client_id` and `parent_property_id` when "None" selected (allows unlinking)

**Created** `frontend/src/pages/properties/DeletePropertyDialog.tsx`
- Accepts `propertyId: string | null` and uses `usePropertyQuery(propertyId)` internally
- Shows warning about child property cascade deletion

**Modified** `frontend/src/components/DataTable.tsx`
- Added `renderExpandedRows?: (row: Row<T>) => ReactNode` prop
- Uses `<Fragment key={row.id}>` to wrap row + expanded content

### 4.5 Routing

**Modified** `frontend/src/App.tsx` — added `/clients` and `/properties` routes
**Modified** `frontend/src/components/Layout.tsx` — added nav items: "Clients" (Users2 icon), "Properties" (Home icon)

---

## Phase 5: Billing & Payments (Backend)

### 5.1 Models

**Create** `backend/app/database/models/invoice.py`
```
InvoiceStatus(str, Enum): draft, sent, paid, overdue, cancelled

Invoice(Base, AuditMixin, TenantMixin):
  id: UUID (PK)
  property_id: UUID FK → properties.id, indexed
  invoice_number: String(50), unique
  status: Enum(InvoiceStatus), default draft
  subtotal: Numeric(10,2), default 0
  discount: Numeric(10,2), default 0          ← invoice-level discount
  tax: Numeric(10,2), default 0
  total: Numeric(10,2), default 0             ← total = subtotal - discount + tax
  issue_date: Date
  due_date: Date
  paid_date: Date, nullable
  notes: Text, nullable
  → property: relationship
  → items: relationship, ordered by sort_order
  → payments: relationship
```

**Create** `backend/app/database/models/invoice_item.py`
```
InvoiceItem(Base, AuditMixin, TenantMixin):
  id: UUID (PK)
  invoice_id: UUID FK → invoices.id, indexed
  service_type_id: UUID FK → service_types.id, nullable
  description: String(500)
  quantity: Numeric(8,2), default 1
  unit_price: Numeric(10,2)
  total: Numeric(10,2)
  sort_order: Integer, default 0
```

**Create** `backend/app/database/models/payment.py`
```
PaymentMethod(str, Enum): cash, bank_transfer, card, other

Payment(Base, AuditMixin, TenantMixin):
  id: UUID (PK)
  invoice_id: UUID FK → invoices.id, indexed
  amount: Numeric(10,2)
  payment_date: Date
  payment_method: Enum(PaymentMethod)
  reference: String(255), nullable
  notes: Text, nullable
  → invoice: relationship
```
Has TenantMixin — payments queried independently for reports.

**Create** `backend/app/database/models/property_service_price.py`
```
PropertyServicePrice(Base, AuditMixin, TenantMixin):
  id: UUID (PK)
  property_id: UUID FK → properties.id, indexed
  service_type_id: UUID FK → service_types.id, indexed
  custom_price: Numeric(10,2)
  UniqueConstraint(property_id, service_type_id)
```

**Modify** `backend/app/database/models/__init__.py`

### 5.2 Migration

Run `alembic revision --autogenerate -m "add billing and payments"`

### 5.3 DTOs

**Create** `backend/app/dto/invoice.py`
- `InvoiceItemRequest(service_type_id?, description, quantity, unit_price, sort_order)`
- `CreateInvoiceRequest(property_id, issue_date, due_date, discount?, tax, notes?, items[])`
- `UpdateInvoiceRequest(status?, issue_date?, due_date?, discount?, tax?, notes?, paid_date?)`
- `InvoiceItemResponse`, `InvoiceResponse` (full with items + payments), `InvoiceListResponse` (lightweight for list view)

**Create** `backend/app/dto/payment.py`
- `CreatePaymentRequest(invoice_id, amount, payment_date, payment_method, reference?, notes?)`
- `PaymentResponse`

**Create** `backend/app/dto/property_service_price.py`
- `SetPropertyServicePriceRequest(property_id, service_type_id, custom_price)`
- `PropertyServicePriceResponse`

### 5.4 Services

**Create** `backend/app/services/invoice_service.py`
- `list_invoices(... status?, property_id?, client_id?)` — filterable, eager load property.client
- `get_invoice` — eager load items, payments, property.client
- `create_invoice` — auto-generate invoice_number, calc line totals (qty * unit_price), subtotal, total (subtotal - discount + tax)
- `update_invoice` — update status/dates/discount/tax/notes. Recalc total if discount or tax changes
- `mark_overdue(db)` — batch: set status=overdue where status=sent and due_date < today
- `delete_invoice` — only allowed for draft/cancelled invoices

**Create** `backend/app/services/payment_service.py`
- `list_payments(... invoice_id?)` — with tenant_filter
- `create_payment` — validates invoice belongs to tenant. If total payments >= invoice total, auto-set invoice status=paid + paid_date
- `delete_payment` — soft delete, revert invoice from paid if needed

**Create** `backend/app/services/property_service_price_service.py`
- `list_prices_for_property(property_id, ...)` — custom prices for a property
- `set_price(body, ...)` — upsert: update if exists, create otherwise
- `delete_price(id, ...)` — remove override (reverts to service type base_price)
- `get_effective_price(property_id, service_type_id, ...)` — returns custom or base price

### 5.5 API Routers

**Create** `backend/app/api/invoices.py` — prefix `/invoices`
| Method | Path | Role | Description |
|--------|------|------|-------------|
| GET | `/invoices` | any auth | List (filters: status, property_id, client_id) |
| GET | `/invoices/{id}` | any auth | Get with items + payments |
| POST | `/invoices` | admin+ | Create with line items |
| PATCH | `/invoices/{id}` | admin+ | Update status/dates/tax |
| DELETE | `/invoices/{id}` | admin+ | Soft delete (draft/cancelled only) |
| POST | `/invoices/mark-overdue` | admin+ | Batch mark overdue |

**Create** `backend/app/api/payments.py` — prefix `/payments`
| Method | Path | Role | Description |
|--------|------|------|-------------|
| GET | `/payments` | any auth | List (filter: invoice_id) |
| POST | `/payments` | admin+ | Record payment |
| DELETE | `/payments/{id}` | admin+ | Soft delete |

**Create** `backend/app/api/property_service_prices.py` — prefix `/property-service-prices`
| Method | Path | Role | Description |
|--------|------|------|-------------|
| GET | `/property-service-prices` | any auth | List for property (query: property_id) |
| POST | `/property-service-prices` | admin+ | Set/update price |
| DELETE | `/property-service-prices/{id}` | admin+ | Remove override |

**Modify** `backend/app/main.py` — register all three routers

---

## Phase 6: Billing & Payments (Frontend)

### 6.1 Types, Services, Hooks

**Create** types: `invoice.ts`, `payment.ts`, `propertyServicePrice.ts`
**Modify** `types/index.ts`
**Create** services: `invoice.service.ts`, `payment.service.ts`, `propertyServicePrice.service.ts`
**Create** hooks: `useInvoices.ts`, `usePayments.ts`, `usePropertyServicePrices.ts`

### 6.2 Schemas

**Modify** `frontend/src/lib/schemas.ts` — add invoice, payment, and pricing schemas

### 6.3 Pages — Invoices

**Create** `frontend/src/pages/invoices/InvoicesPage.tsx` — columns: Invoice #, Client, Property, Status (color-coded badge), Total, Issue Date, Due Date, Actions. Filter dropdowns for status/property/client. "Mark Overdue" button for admins.

Status badge colors: draft=gray, sent=blue, paid=green, overdue=red, cancelled=gray-outline

**Create** `frontend/src/pages/invoices/InvoiceColumns.tsx`
**Create** `frontend/src/pages/invoices/CreateInvoiceDialog.tsx` — the most complex dialog:
  - Property selector dropdown
  - Issue date + due date
  - Dynamic line items: service type selector (auto-fills description + unit_price from effective price), description, quantity, unit_price. Add/remove rows.
  - Auto-calculated subtotal, discount input, tax input, total (subtotal - discount + tax)
  - Notes textarea
**Create** `frontend/src/pages/invoices/EditInvoiceDialog.tsx` — status, dates, discount, tax, notes
**Create** `frontend/src/pages/invoices/DeleteInvoiceDialog.tsx` — only for draft/cancelled
**Create** `frontend/src/pages/invoices/InvoiceDetailDialog.tsx` — read-only view with line items table + payments list + "Record Payment" button

### 6.4 Pages — Payments

**Create** `frontend/src/pages/payments/PaymentsPage.tsx` — columns: Invoice #, Amount, Date, Method (badge), Reference, Actions
**Create** `frontend/src/pages/payments/PaymentColumns.tsx`
**Create** `frontend/src/pages/payments/CreatePaymentDialog.tsx` — invoice selector, amount, date, method, reference, notes
**Create** `frontend/src/pages/payments/DeletePaymentDialog.tsx`

### 6.5 Routing

**Modify** `frontend/src/App.tsx` — add `/invoices` and `/payments` routes
**Modify** `frontend/src/components/Layout.tsx` — add nav items: "Invoices" (FileText icon), "Payments" (CreditCard icon)

---

## Verification Plan

After each phase:
1. **Backend**: `docker-compose --profile test up test --build` to run existing tests + verify no regressions
2. **Backend**: Use `docker-compose up --build` and test endpoints manually via curl/browser DevTools
3. **Frontend**: Check pages render, CRUD operations work, forms validate correctly
4. **End-to-end after all phases**: Login → create service type with checklist → create client → create property (including building with apartments) → create invoice for property with line items → record payment → verify status auto-updates to paid → verify overdue flagging

---

## Key Reference Files (existing patterns to follow)

- `backend/app/database/base.py` — Base, AuditMixin, TenantMixin
- `backend/app/services/user_service.py` — service pattern (tenant_filter, soft delete, pagination tuple)
- `backend/app/api/users.py` — router pattern (CRUD, role guards, pagination, DTO mapping)
- `backend/app/dto/user.py` — DTO pattern (from_entity, request/response split)
- `frontend/src/pages/users/UsersPage.tsx` — page pattern (DataTable, dialog state, hooks)
- `frontend/src/hooks/useUsers.ts` — hook pattern (query keys, mutations, toast, invalidation)
- `frontend/src/lib/schemas.ts` — Zod schema patterns
