# Plan: Add Unit Property Type & Restrict Apartment to Parent-Only

## Context

Currently the property system has 4 types: `house`, `apartment`, `building`, `commercial`. Apartments serve as child properties of buildings (and can also exist standalone). We want to introduce a new **Unit** property type that takes over the "child property" role, while **Apartment** becomes a parent-only type (like house/building/commercial).

**Key rules after this change:**
- **Unit** is the only property type that can be added as a child of another property
- **Apartment** stays in the system but can only be a parent/standalone property (cannot have `parent_property_id`)
- Building creation auto-generates **Units** (not Apartments)
- All other types (house, building, commercial, apartment) can be parents but not children

---

## Phase 1: Backend — Model & Migration

### 1.1 Add `unit` to PropertyType enum

**Modified** `backend/app/database/models/property.py`
- Add `unit = "unit"` to the `PropertyType` enum

### 1.2 Migration

**Created** `backend/app/database/migrations/versions/YYYYMMDDhhmm_add_unit_property_type.py`
- Add `unit` to the `property_type_enum` PostgreSQL enum using `ALTER TYPE property_type_enum ADD VALUE 'unit'`
- Convert existing child apartments to units: `UPDATE properties SET property_type = 'unit' WHERE parent_property_id IS NOT NULL AND property_type = 'apartment'`
- This ensures existing data is consistent with the new rules (apartments with a parent become units)

---

## Phase 2: Backend — Service & DTO Changes

### 2.1 DTOs

**Modified** `backend/app/dto/property.py`
- Rename `number_of_apartments` to `number_of_units` in `CreatePropertyRequest` (field + validation stays `ge=1, le=100`)

### 2.2 Property Service

**Modified** `backend/app/services/property_service.py`

**`create_property`:**
- Change parent validation: only `unit` type can have a `parent_property_id`. If `body.parent_property_id` is set and `body.property_type != PropertyType.unit`, raise error "Only units can be added as children of other properties"
- Remove the old check "apartment cannot be part of another apartment" — replaced by the new rule above
- The parent itself can be any type except `unit` (a unit cannot be a parent of other units)
- Rename `number_of_apartments` references to `number_of_units`
- Auto-generation creates `PropertyType.unit` children named `"Unit 1"`, `"Unit 2"`, etc. instead of `"Apartment 1"`, `"Apartment 2"`
- Rename validation error: `number_of_units` can only be specified for building type

**`update_property`:**
- Change parent validation: if `parent_property_id` is being set, the property being edited must be a `unit` type
- Parent cannot be a `unit` type (units can't have children)
- Remove old "apartment cannot be part of another apartment" check

**`delete_property`:**
- No changes needed — already soft-deletes child properties generically (comment can be updated from "apartments in a building" to "child properties")

### 2.3 API

**Modified** `backend/app/api/properties.py`
- No structural changes — just ensure `property_type` filter works with the new `unit` value (it should, since it uses the enum directly)

---

## Phase 3: Backend — Seed Script

**Modified** `backend/scripts/seed.py`
- Change all `_APT_ROWS` entries from `"property_type": "apartment"` to `"property_type": "unit"`
- Rename helper `_apt_id` to `_unit_id` for clarity
- Rename variable `_APT_ROWS` to `_UNIT_ROWS`
- Change child property names from `f"Apt {u}"` to `f"Unit {u}"`
- The standalone apartment (prop 10, "Studio Central") stays as `"apartment"` type with `parent_property_id: None` — this is now correct since apartments are standalone/parent only
- Update apartment-level override comments to "Unit-level override"

---

## Phase 4: Frontend — Types & Schemas

### 4.1 Types

**Modified** `frontend/src/types/property.ts`
- Add `"unit"` to `PropertyType` union: `"house" | "apartment" | "building" | "commercial" | "unit"`
- Rename `number_of_apartments` to `number_of_units` in `PropertyCreatePayload`

### 4.2 Schemas

**Modified** `frontend/src/lib/schemas.ts`
- Add `"unit"` to the property type z.enum in both `createPropertySchema` and `editPropertySchema`
- Rename `number_of_apartments` to `number_of_units` in `createPropertySchema`

---

## Phase 5: Frontend — Property Pages

### 5.1 CreatePropertyDialog

**Modified** `frontend/src/pages/properties/CreatePropertyDialog.tsx`
- Add `<SelectItem value="unit">Unit</SelectItem>` to the type dropdown
- Change building auto-generation section:
  - Rename field from `number_of_apartments` to `number_of_units`
  - Label: "Number of Units" (was "Number of Apartments")
  - Info message: "Units will be auto-created and linked to this building with the same address and client."
- Change the "Part of" (parent selector) section:
  - Show when `propertyType === "unit"` instead of `propertyType === "apartment"`
  - Info message: "Link this unit to a building or property it belongs to."
  - Filter parent options: exclude `unit` type (units can't be parents)
- Submit handler: use `number_of_units` field name

### 5.2 EditPropertyDialog

**Modified** `frontend/src/pages/properties/EditPropertyDialog.tsx`
- Add `<SelectItem value="unit">Unit</SelectItem>` to the type dropdown
- Change the "Part of" section to show when `propertyType === "unit"` (was `"apartment"`)
- Filter parent options: exclude `unit` type
- Info message: "Link this unit to a building or property it belongs to."
- Submit handler: send `parent_property_id` only when type is `"unit"` (was `"apartment"`)

### 5.3 PropertiesPage

**Modified** `frontend/src/pages/properties/PropertiesPage.tsx`
- Add `unit: "Unit"` to `typeLabels` record
- Add `<SelectItem value="unit">Unit</SelectItem>` to type filter dropdown

### 5.4 PropertyColumns

**Modified** `frontend/src/pages/properties/PropertyColumns.tsx`
- Add `unit: "Unit"` to `typeLabels` record

### 5.5 PropertyCardView

**Modified** `frontend/src/pages/properties/PropertyCardView.tsx`
- Add `unit` to `typeIcons` (use `DoorOpen` or `Hash` from lucide-react — pick an icon that distinguishes from apartment)
- Add `unit: "Unit"` to `typeLabels`
- Change collapsible trigger text: currently says `{count} apartment{s}` — change to `{count} unit{s}`

---

## Phase 6: Frontend — Invoice Pages

### 6.1 GenerateInvoicesDialog

**Modified** `frontend/src/pages/invoices/GenerateInvoicesDialog.tsx`
- No changes needed — already uses generic "units" label in the property selector suffix and doesn't reference apartment specifically

### 6.2 InvoiceColumns / InvoicesPage

- No changes needed — these reference properties generically

---

## Summary of All Files Changed

| File | Change |
|------|--------|
| `backend/app/database/models/property.py` | Add `unit` to enum |
| `backend/app/database/migrations/versions/...` | New migration: add enum value + convert existing child apartments |
| `backend/app/dto/property.py` | Rename `number_of_apartments` → `number_of_units` |
| `backend/app/services/property_service.py` | New parent/child validation rules, generate Units not Apartments |
| `backend/scripts/seed.py` | Child properties use `unit` type, rename vars |
| `frontend/src/types/property.ts` | Add `unit` to type, rename payload field |
| `frontend/src/lib/schemas.ts` | Add `unit` to enum, rename field |
| `frontend/src/pages/properties/CreatePropertyDialog.tsx` | Unit in dropdown, "Part of" for unit, generate units |
| `frontend/src/pages/properties/EditPropertyDialog.tsx` | Unit in dropdown, "Part of" for unit |
| `frontend/src/pages/properties/PropertiesPage.tsx` | Unit in filter + labels |
| `frontend/src/pages/properties/PropertyColumns.tsx` | Unit label |
| `frontend/src/pages/properties/PropertyCardView.tsx` | Unit icon + label + collapsible text |

---

## Validation Rules Summary (After Change)

| Rule | Before | After |
|------|--------|-------|
| Can be a child (have parent_property_id) | apartment | unit |
| Can be a parent (have children) | house, building, commercial | house, apartment, building, commercial |
| Cannot be a parent | apartment | unit |
| Auto-generated children when creating building | apartments | units |
| Auto-generated child names | "Apartment 1", "Apartment 2" | "Unit 1", "Unit 2" |
| DTO field for generation count | `number_of_apartments` | `number_of_units` |
