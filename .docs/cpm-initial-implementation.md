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

## Phase 4b: Properties Card View & Bug Fix ✅

### 4b.1 Card View

**Created** `frontend/src/pages/properties/PropertyCardView.tsx`
- `PropertyCardView` — responsive grid (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`) of property cards
- `PropertyCard` — shows property type icon (Home/Building/Building2/Store from lucide-react), name, type badge, address/city with MapPin icon, client name with User icon, status as subtle dot (emerald for active, gray for inactive) + text
- Collapsible children section using Radix `Collapsible` — shows apartment count, expands to list children with name, client name, and actions menu. Inactive children shown with muted + strikethrough name
- `ActionsMenu` — shared edit/delete dropdown used by both parent cards and child rows
- Empty state: centered "No properties found." matching DataTable style

**Modified** `frontend/src/pages/properties/PropertiesPage.tsx`
- Added `ViewMode` type (`"card" | "table"`) with localStorage persistence (`properties-view-mode` key)
- Default view is card (when no localStorage value exists)
- View toggle: `LayoutGrid` and `List` icon buttons after filters, pushed right with `ml-auto`. Active button uses `variant="secondary"`, inactive uses `variant="ghost"`
- Conditional rendering: `PropertyCardView` for card mode, existing `DataTable` for table mode
- Both views share the same data, filters, and create/edit/delete dialogs

### 4b.2 Backend Bug Fix

**Modified** `backend/app/services/property_service.py`
- Fixed `MissingGreenlet` error caused by lazy loading `client` relationship on child properties
- Added chained eager load: `selectinload(Property.child_properties).selectinload(Property.client)` in both `list_properties` and `get_property` queries
- Previously, `PropertySummaryResponse.from_entity(child)` accessed `prop.client` on child properties that were only loaded via `selectinload(Property.child_properties)` without their own `client` relationship being eager-loaded

---

## Phase 5a: Property-Service Assignment (Backend) ✅

### Key Design Decisions

- **Invoicing unit = "leaf" property**: If a property has children → each child gets invoiced. If no children → the property itself is invoiced. Works for all types (building+apartments, house+apartments, standalone house/commercial).
- **Dynamic service inheritance**: Services assigned to parent properties via `PropertyServiceType` records. Children inherit at query time (no DB records on children). A child can have its own record to override price or opt out (`is_active=false`).
- **Override deletion**: Child override records are hard deleted (lightweight, can be recreated). Parent direct assignments are soft deleted via `deleted_at` (standard pattern).
- **Effective services include inactive**: `get_effective_services` returns all services including inactive ones (with `is_active` flag). This allows the UI to show inherited services with an off toggle rather than hiding them. Invoice generation filters out inactive services itself.
- **Service badges embedded in property response**: Lightweight `ServiceBadge` data (service_type_name, effective_price, is_active) is computed from eager-loaded relationships and embedded in `PropertyResponse`/`PropertySummaryResponse`. Eliminates N+1 API calls for displaying badges.
- **Price snapshot on invoice creation**: `InvoiceItem.unit_price` is frozen at creation time. Changing `ServiceType.base_price` or `PropertyServiceType.custom_price` only affects future invoices.
- **Both periodic and ad-hoc invoicing**: Invoices have optional `period_start`/`period_end` for monthly billing, plus manual creation with custom line items.

### 5a.1 Model

**Created** `backend/app/database/models/property_service_type.py`
```
PropertyServiceType(Base, AuditMixin, TenantMixin):
  id: UUID PK
  property_id: UUID FK → properties.id, indexed
  service_type_id: UUID FK → service_types.id, indexed
  custom_price: Numeric(10,2), nullable  — null = use ServiceType.base_price
  is_active: Boolean, default True       — false = opt out of inherited service
  Partial unique Index on (property_id, service_type_id) WHERE deleted_at IS NULL
  → property: relationship (back_populates="service_assignments")
  → service_type: relationship
```

**Modified** `backend/app/database/models/property.py` — added `service_assignments` relationship to Property model

**Modified** `backend/app/database/models/__init__.py` — added `PropertyServiceType`

### 5a.2 Migration

**Created** `backend/app/database/migrations/versions/202602210001_add_property_service_types.py`
- `property_service_types` table with indexes on property_id, service_type_id, tenant_id
- Partial unique index `uq_property_service_type_active`

### 5a.3 DTOs

**Created** `backend/app/dto/property_service_type.py`
- `AssignServiceRequest(property_id, service_type_id, custom_price?, is_active=True)` — is_active allows creating an override that opts out in one step
- `BulkAssignServicesRequest(property_id, service_type_ids[])`
- `UpdatePropertyServiceRequest(custom_price?, is_active?)` — uses `model_fields_set` for nullable custom_price
- `PropertyServiceTypeResponse(id, property_id, service_type_id, service_type_name, custom_price, effective_price, is_active, is_inherited)` with `from_entity()`
- `EffectiveServiceResponse(service_type_id, service_type_name, effective_price, is_active, is_inherited, override_id?)` — includes is_active so UI can show toggle state

**Modified** `backend/app/dto/property.py`
- Added `ServiceBadgeItem(service_type_name, effective_price, is_active)` DTO
- Added `_compute_service_badges(prop, parent_assignments?)` helper — computes effective service badges from eager-loaded relationships (parent + child override merge)
- Added `services: list[ServiceBadgeItem]` field to both `PropertySummaryResponse` and `PropertyResponse`
- `PropertyResponse.from_entity` passes own service_assignments as `parent_assignments` to child `PropertySummaryResponse.from_entity` for inheritance computation

### 5a.4 Service

**Created** `backend/app/services/property_service_type_service.py`
- `list_assignments(property_id, ...)` — direct assignments for a property
- `get_effective_services(property_id, ...)` — **key method**: resolves inherited + direct services with effective prices. Returns all services including inactive ones (with `is_active` flag)
  - Logic: get direct assignments → if property has parent, get parent's assignments → merge (child overrides parent) → compute effective_price (custom_price ?? parent's custom_price ?? base_price)
- `assign_service(body, ...)` — validate property + service_type, check for duplicates, uses `body.is_active`
- `bulk_assign_services(body, ...)` — assign multiple services at once, skipping already-assigned
- `update_assignment(id, body, ...)` — update custom_price or is_active
- `remove_assignment(id, ...)` — **hard delete** for child override records (`db.delete()`), **soft delete** for parent direct assignments

**Modified** `backend/app/services/property_service.py` — added eager loading of `service_assignments → service_type` in both `list_properties` and `get_property` (chained through child_properties too)

### 5a.5 API Router

**Created** `backend/app/api/property_service_types.py` — prefix `/property-service-types`
| Method | Path | Role | Description |
|--------|------|------|-------------|
| GET | `?property_id=X` | any auth | List direct assignments for a property |
| GET | `/effective?property_id=X` | any auth | Get effective services (with inheritance) |
| POST | `/` | admin+ | Assign service to property |
| POST | `/bulk` | admin+ | Bulk assign services |
| PATCH | `/{id}` | admin+ | Update assignment (custom_price, is_active) |
| DELETE | `/{id}` | admin+ | Remove assignment |

**Modified** `backend/app/main.py` — registered `property_service_types` router

### 5a.6 Seed Data

**Modified** `backend/scripts/seed.py` — added 23 property-service assignments:
- Buildings 1–4, 6, 7 with various service combinations and custom prices
- House with Regular + Deep + Window (custom price on window)
- Commercial hotel with all 4 services at custom prices
- Standalone apartment with Move-in/Move-out + Regular
- 2 apartment-level overrides: Apt 1/Building 1 custom price ($95), Apt 2/Building 3 opts out of Carpet

---

## Phase 5b: Invoicing & Payments (Backend) ✅

### 5b.1 Models

**Created** `backend/app/database/models/invoice.py`
```
InvoiceStatus(str, Enum): draft, sent, paid, overdue, cancelled

Invoice(Base, AuditMixin, TenantMixin):
  id: UUID PK
  property_id: UUID FK → properties.id, indexed
  invoice_number: String(50)
  status: Enum(InvoiceStatus), default draft
  period_start: Date, nullable    — for periodic invoices
  period_end: Date, nullable      — for periodic invoices
  subtotal: Numeric(10,2), default 0
  discount: Numeric(10,2), default 0
  tax: Numeric(10,2), default 0
  total: Numeric(10,2), default 0
  issue_date: Date
  due_date: Date
  paid_date: Date, nullable
  notes: Text, nullable
  → property: relationship
  → items: relationship (ordered by sort_order)
  → payments: relationship
  UniqueConstraint(tenant_id, invoice_number) partial where deleted_at IS NULL
```

**Created** `backend/app/database/models/invoice_item.py`
```
InvoiceItem(Base, AuditMixin, TenantMixin):
  id: UUID PK
  invoice_id: UUID FK → invoices.id, indexed
  service_type_id: UUID FK → service_types.id, nullable  — null for ad-hoc items
  description: String(500)
  quantity: Numeric(8,2), default 1
  unit_price: Numeric(10,2)    — SNAPSHOTTED at creation time
  total: Numeric(10,2)         — quantity * unit_price
  sort_order: Integer, default 0
```

**Created** `backend/app/database/models/payment.py`
```
PaymentMethod(str, Enum): cash, bank_transfer, card, other

Payment(Base, AuditMixin, TenantMixin):
  id: UUID PK
  invoice_id: UUID FK → invoices.id, indexed
  amount: Numeric(10,2)
  payment_date: Date
  payment_method: Enum(PaymentMethod)
  reference: String(255), nullable
  notes: Text, nullable
  → invoice: relationship
```

**Modified** `backend/app/database/models/__init__.py` — added Invoice, InvoiceItem, Payment

### 5b.2 Migration

**Created** `backend/app/database/migrations/versions/202602210002_add_invoices_and_payments.py`

### 5b.3 DTOs

**Created** `backend/app/dto/invoice.py`
- `InvoiceItemRequest(service_type_id?, description, quantity, unit_price, sort_order)`
- `CreateInvoiceRequest(property_id, issue_date, due_date, period_start?, period_end?, discount?, tax?, notes?, items[])`
- `UpdateInvoiceRequest(status?, issue_date?, due_date?, discount?, tax?, notes?, paid_date?)`
- `GenerateInvoicesRequest(property_id, issue_date, due_date, period_start?, period_end?, discount?, tax?, notes?)` — batch generate for a parent's children using effective services
- `InvoiceItemResponse` with `from_entity()`
- `InvoiceResponse` — full with items + payments + property_name + client_name
- `InvoiceListResponse` — lightweight for list view (no items/payments)

**Created** `backend/app/dto/payment.py`
- `CreatePaymentRequest(invoice_id, amount, payment_date, payment_method, reference?, notes?)`
- `UpdatePaymentRequest(amount?, payment_date?, payment_method?, reference?, notes?)`
- `PaymentResponse` with `from_entity()`

### 5b.4 Services

**Created** `backend/app/services/invoice_service.py`
- `list_invoices(... status?, property_id?, client_id?)` — filterable, eager load property.client
- `get_invoice(id, ...)` — eager load items, payments, property.client
- `create_invoice(body, ...)` — auto-generate invoice_number (tenant-scoped sequential: INV-YYYYMM-0001), calc line totals, subtotal, total
- `update_invoice(id, body, ...)` — partial update. Recalc total if discount/tax change
- `generate_invoices(body, ...)` — **key method for batch generation**:
  1. Load property, check if it has children
  2. If has children: for each active child, resolve effective services (filters out inactive), create invoice with items
  3. If no children: resolve effective services for the property itself, create single invoice
  4. Each item snapshots effective price at this moment
  5. Return list of created invoices
- `mark_overdue(db)` — batch: set status=overdue where status=sent and due_date < today
- `delete_invoice(id, ...)` — soft delete, only allowed for draft/cancelled

**Created** `backend/app/services/payment_service.py`
- `list_payments(... invoice_id?)` — with tenant_filter
- `create_payment(body, ...)` — validate invoice belongs to tenant. Auto-set invoice status=paid + paid_date when total payments >= invoice total
- `delete_payment(id, ...)` — soft delete, revert invoice from paid if total payments < invoice total after deletion

### 5b.5 API Routers

**Created** `backend/app/api/invoices.py` — prefix `/invoices`
| Method | Path | Role | Description |
|--------|------|------|-------------|
| GET | `/` | any auth | List (filters: status, property_id, client_id) |
| GET | `/{id}` | any auth | Get with items + payments |
| POST | `/` | admin+ | Create with line items |
| POST | `/generate` | admin+ | Batch generate from effective services |
| PATCH | `/{id}` | admin+ | Update status/dates/tax |
| DELETE | `/{id}` | admin+ | Soft delete (draft/cancelled only) |
| POST | `/mark-overdue` | admin+ | Batch mark overdue |

**Created** `backend/app/api/payments.py` — prefix `/payments`
| Method | Path | Role | Description |
|--------|------|------|-------------|
| GET | `/` | any auth | List (filter: invoice_id) |
| POST | `/` | admin+ | Record payment |
| DELETE | `/{id}` | admin+ | Soft delete |

**Modified** `backend/app/main.py` — registered invoices + payments routers

---

## Phase 5c: Property-Service Assignment (Frontend) ✅

### 5c.1 Types, Services, Hooks

**Created** `frontend/src/types/propertyServiceType.ts` — PropertyServiceType, EffectiveService, AssignServicePayload, BulkAssignServicesPayload, UpdatePropertyServicePayload
**Modified** `frontend/src/types/property.ts` — added `ServiceBadge` interface (`service_type_name`, `effective_price`, `is_active`), added `services: ServiceBadge[]` to both `Property` and `PropertySummary`
**Modified** `frontend/src/types/index.ts` — added re-exports for propertyServiceType types and ServiceBadge
**Created** `frontend/src/services/propertyServiceType.service.ts` — getAssignments, getEffectiveServices, assignService, bulkAssignServices, updateAssignment, removeAssignment
**Created** `frontend/src/hooks/usePropertyServiceTypes.ts` — query keys `["property-service-types"]`, `["effective-services"]`. All mutations invalidate `["properties"]` key so embedded service badges auto-refresh

### 5c.2 UI — ManageServicesDialog

**Created** `frontend/src/pages/properties/ManageServicesDialog.tsx`
- Two modes based on property type:
  - **Parent/standalone properties**: Shows `DirectServiceRow` components for direct assignments — custom price input, remove button. `AddServiceRow` at bottom via SearchableSelect
  - **Child properties**: Shows `EffectiveServiceRow` components with inheritance badges ("Inherited" indicator), toggle switch to activate/deactivate inherited services (creates override with `is_active=false`), custom price override input
- Uses both `usePropertyServiceTypesQuery` (for direct assignments/mutations) and `useEffectiveServicesQuery` (for display with inheritance)

### 5c.3 UI — Service Badges

**Created** `frontend/src/pages/properties/ServiceBadges.tsx` — pure render component (no API calls), takes `services: ServiceBadge[]` prop. Shows abbreviated badges (first letters of each word, e.g. "RC" for Regular Cleaning) with tooltip on hover showing full name + effective price
**Created** `frontend/src/components/ui/tooltip.tsx` — Radix Tooltip component (installed `@radix-ui/react-tooltip`)
**Modified** `frontend/src/App.tsx` — wrapped app in `TooltipProvider`

### 5c.4 Integration with Property Views

**Modified** `frontend/src/pages/properties/PropertiesPage.tsx`
- Added `servicesTargetId` state + `ManageServicesDialog`
- "Manage Services" action in expanded child row dropdown menus
- `ServiceBadges` in expanded child rows using `services={child.services}`

**Modified** `frontend/src/pages/properties/PropertyColumns.tsx`
- Added `onManageServices` callback, "Manage Services" dropdown item
- "Services" column using `<ServiceBadges services={row.original.services} />`

**Modified** `frontend/src/pages/properties/PropertyCardView.tsx`
- Added `onManageServices` prop threaded through PropertyCardView → PropertyCard → ChildRow → ActionsMenu
- `ServiceBadges` displayed in card content and child rows

### 5c.5 Routing

No new routes — services management is part of the property UI via dialog.

---

## Phase 6: Invoicing & Payments (Frontend) ✅

### 6.1 Types, Services, Hooks

**Created** `frontend/src/types/invoice.ts` — InvoiceStatus, Invoice, InvoiceListItem (with `parent_property_name`), InvoiceItem, PaymentSummary, CreateInvoicePayload, UpdateInvoicePayload, GenerateInvoicesPayload
**Created** `frontend/src/types/payment.ts`
**Modified** `frontend/src/types/index.ts` — added re-exports
**Created** `frontend/src/services/invoice.service.ts` — getInvoices (with search/status/property_id/client_id params), getInvoice, createInvoice, generateInvoices, updateInvoice, deleteInvoice, markOverdue, bulkUpdateStatus, bulkDelete
**Created** `frontend/src/services/payment.service.ts`
**Created** `frontend/src/hooks/useInvoices.ts` — list key `["invoices"]`, detail key `["invoice"]`. Hooks: useInvoicesQuery, useInvoiceQuery, useCreateInvoice, useGenerateInvoices, useUpdateInvoice, useDeleteInvoice, useBulkUpdateStatus, useBulkDeleteInvoices, useMarkOverdue
**Created** `frontend/src/hooks/usePayments.ts`

### 6.2 Schemas

**Modified** `frontend/src/lib/schemas.ts` — added invoice, payment, generate schemas

### 6.3 Pages — Invoices

**Created** `frontend/src/pages/invoices/InvoicesPage.tsx`
- Columns: Checkbox (select), Invoice #, Client, Property, Parent, Status (color-coded badge), Total, Issue Date, Due Date, Actions
- Filter bar: search input (debounced 300ms, server-side ilike on invoice_number), status dropdown, property dropdown (parents only — selecting a parent shows invoices for that property + all children), client dropdown (SearchableSelect)
- Row selection via TanStack Table `enableRowSelection` with `getRowId` for stable IDs
- Bulk actions toolbar: appears when rows selected — "N selected" count, Actions dropdown (Change Status sub-menu with all 5 statuses, Delete), clear selection button
- Confirmation dialog (AlertDialog) before executing bulk operations, with destructive styling for delete
- Bulk mutations use `Promise.allSettled` for partial failure handling — toast shows success/fail counts
- Loading state is inline (only table area) to prevent filter bar unmounting and losing input focus

**Created** `frontend/src/pages/invoices/InvoiceColumns.tsx` — checkbox column (header: select all with indeterminate, cell: select row), invoice number as clickable link, client (muted), property, parent property (muted, "—" when null), status badge (Draft=outline, Sent=default, Paid=emerald, Overdue=destructive, Cancelled=secondary), total, issue date, due date, actions dropdown (View, Edit, Delete for draft/cancelled)
**Created** `frontend/src/pages/invoices/CreateInvoiceDialog.tsx` — property selector, dates, dynamic line items with service type auto-fill, auto-calculated totals
**Created** `frontend/src/pages/invoices/GenerateInvoicesDialog.tsx` — select parent property, dates, generates invoices for children using effective services
**Created** `frontend/src/pages/invoices/EditInvoiceDialog.tsx` — status, dates, discount, tax, notes
**Created** `frontend/src/pages/invoices/DeleteInvoiceDialog.tsx` — only for draft/cancelled
**Created** `frontend/src/pages/invoices/InvoiceDetailDialog.tsx` — read-only view with line items table + payments list + "Record Payment" button

**Created** `frontend/src/components/ui/checkbox.tsx` — shadcn Checkbox component (Radix-based), used for table row selection

### 6.4 Pages — Payments

**Created** `frontend/src/pages/payments/PaymentsPage.tsx` — columns: Invoice #, Amount, Date, Method (badge), Reference, Actions
**Created** `frontend/src/pages/payments/PaymentColumns.tsx`
**Created** `frontend/src/pages/payments/CreatePaymentDialog.tsx` — invoice selector, amount, date, method, reference, notes
**Created** `frontend/src/pages/payments/DeletePaymentDialog.tsx`

### 6.5 Routing

**Modified** `frontend/src/App.tsx` — added `/invoices` and `/payments` routes
**Modified** `frontend/src/components/Layout.tsx` — added nav items: "Invoices" (FileText icon), "Payments" (CreditCard icon)

### 6.6 Backend Enhancements (done alongside frontend)

**Modified** `backend/app/services/invoice_service.py`
- Invoice number generation uses issue date (not `now()`) for the `YYYYMM` prefix — allows creating future-dated invoices with correct numbering
- List invoices sorted by `invoice_number` desc (was `created_at` desc)
- Added `search` parameter — `ilike` filter on `invoice_number`
- Property filter now includes child properties: `OR(property_id = X, property_id IN (children of X))` — selecting a parent in the dropdown shows all its children's invoices too
- Added eager load for `property.parent_property` in list query

**Modified** `backend/app/api/invoices.py` — added `search` query parameter

**Modified** `backend/app/dto/invoice.py`
- `InvoiceListResponse` — added `parent_property_name: str | None` field, populated from `inv.property.parent_property.name`

---

## Verification Plan

After each phase:
1. **Backend**: `docker-compose --profile test up test --build` to run existing tests + verify no regressions
2. **Backend**: Use `docker-compose up --build` and test endpoints manually via curl/browser DevTools
3. **Frontend**: Check pages render, CRUD operations work, forms validate correctly
4. **End-to-end after all phases**: Login → assign services to a building → verify apartments inherit → generate invoices for building (creates one per apartment) → create manual invoice for standalone house → change service base_price → verify old invoices unchanged, new invoices use new price → record payment → verify auto-paid status → mark overdue → verify sent invoices past due_date get flagged

---

## Key Reference Files (existing patterns to follow)

- `backend/app/database/base.py` — Base, AuditMixin, TenantMixin
- `backend/app/services/user_service.py` — service pattern (tenant_filter, soft delete, pagination tuple)
- `backend/app/services/property_service_type_service.py` — effective services resolution pattern
- `backend/app/api/users.py` — router pattern (CRUD, role guards, pagination, DTO mapping)
- `backend/app/dto/user.py` — DTO pattern (from_entity, request/response split)
- `backend/app/dto/property_service_type.py` — DTO pattern with computed fields (effective_price, is_inherited)
- `frontend/src/pages/users/UsersPage.tsx` — page pattern (DataTable, dialog state, hooks)
- `frontend/src/hooks/useUsers.ts` — hook pattern (query keys, mutations, toast, invalidation)
- `frontend/src/lib/schemas.ts` — Zod schema patterns
