"""
Seed script — populates the database with sample data.

Run inside the backend container:
    docker-compose exec backend python -m scripts.seed

Idempotent: skips inserts if data already exists (checks service_types table).
"""

import asyncio
import uuid
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session

# ---------------------------------------------------------------------------
# Shared tenant
# ---------------------------------------------------------------------------
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# ---------------------------------------------------------------------------
# Service types
# ---------------------------------------------------------------------------
ST_REGULAR = uuid.UUID("10000000-0000-0000-0000-000000000001")
ST_DEEP = uuid.UUID("10000000-0000-0000-0000-000000000002")
ST_WINDOW = uuid.UUID("10000000-0000-0000-0000-000000000003")
ST_CARPET = uuid.UUID("10000000-0000-0000-0000-000000000004")
ST_MOVEINOUT = uuid.UUID("10000000-0000-0000-0000-000000000005")

SERVICE_TYPES = [
    {"id": ST_REGULAR, "name": "Regular Cleaning", "description": "Standard recurring cleaning service including dusting, vacuuming, mopping, and bathroom sanitization.", "base_price": 80.00, "estimated_duration_minutes": 120, "is_active": True, "tenant_id": TENANT_ID},
    {"id": ST_DEEP, "name": "Deep Cleaning", "description": "Thorough cleaning covering hard-to-reach areas, appliance interiors, grout scrubbing, and detailed sanitization.", "base_price": 180.00, "estimated_duration_minutes": 240, "is_active": True, "tenant_id": TENANT_ID},
    {"id": ST_WINDOW, "name": "Window Cleaning", "description": "Interior and exterior window washing, frame wiping, and sill cleaning.", "base_price": 60.00, "estimated_duration_minutes": 90, "is_active": True, "tenant_id": TENANT_ID},
    {"id": ST_CARPET, "name": "Carpet Cleaning", "description": "Professional carpet shampooing, stain treatment, and deodorizing.", "base_price": 120.00, "estimated_duration_minutes": 150, "is_active": True, "tenant_id": TENANT_ID},
    {"id": ST_MOVEINOUT, "name": "Move-in/Move-out Cleaning", "description": "Complete property cleaning for tenant transitions including appliance cleaning, cabinet wipe-down, and full sanitization.", "base_price": 250.00, "estimated_duration_minutes": 300, "is_active": True, "tenant_id": TENANT_ID},
]

# ---------------------------------------------------------------------------
# Checklist items (per service type)
# ---------------------------------------------------------------------------
_ci_counter = 0


def _ci_id() -> uuid.UUID:
    global _ci_counter
    _ci_counter += 1
    return uuid.UUID(f"11000000-0000-0000-0000-{_ci_counter:012d}")


CHECKLIST_ITEMS = []

for st_id, items in [
    (ST_REGULAR, [
        ("Dust surfaces", "Dust all accessible surfaces including shelves, counters, and furniture"),
        ("Vacuum floors", "Vacuum all carpeted areas and rugs"),
        ("Mop hard floors", "Mop all hard floor surfaces"),
        ("Clean bathrooms", "Scrub toilets, sinks, showers, and mirrors"),
        ("Empty trash bins", "Empty and reline all waste bins"),
    ]),
    (ST_DEEP, [
        ("Clean inside appliances", "Oven, microwave, and refrigerator interior cleaning"),
        ("Scrub grout and tile", "Deep scrub bathroom and kitchen tile grout"),
        ("Clean light fixtures", "Remove and clean light fixtures and ceiling fans"),
        ("Wash baseboards", "Wipe down all baseboards throughout the property"),
        ("Sanitize high-touch surfaces", "Disinfect door handles, switches, and remotes"),
    ]),
    (ST_WINDOW, [
        ("Clean interior glass", "Wash all interior window panes"),
        ("Clean exterior glass", "Wash all exterior window panes"),
        ("Wipe frames and sills", "Clean window frames, tracks, and sills"),
    ]),
    (ST_CARPET, [
        ("Pre-treat stains", "Apply stain remover to visible spots"),
        ("Shampoo carpets", "Machine shampoo all carpeted areas"),
        ("Deodorize", "Apply deodorizing treatment to carpets"),
    ]),
    (ST_MOVEINOUT, [
        ("Clean all cabinets", "Wipe inside and outside of all cabinets and drawers"),
        ("Clean appliances", "Deep clean oven, fridge, dishwasher, and washer/dryer"),
        ("Sanitize bathrooms", "Full bathroom sanitization including fixtures and tile"),
        ("Clean windows and blinds", "Wash windows and dust or wipe blinds"),
        ("Final walkthrough", "Inspect all rooms and touch up as needed"),
    ]),
]:
    for order, (name, desc) in enumerate(items, start=1):
        CHECKLIST_ITEMS.append({
            "id": _ci_id(),
            "service_type_id": st_id,
            "name": name,
            "description": desc,
            "sort_order": order,
            "tenant_id": TENANT_ID,
        })

# ---------------------------------------------------------------------------
# Clients (12)
# ---------------------------------------------------------------------------
def _client_id(n: int) -> uuid.UUID:
    return uuid.UUID(f"20000000-0000-0000-0000-{n:012d}")


CLIENTS = [
    {"id": _client_id(1), "name": "Marko Petrovski", "email": "marko.petrovski@example.com", "phone": "+389 70 123 456", "address": "Bul. Partizanski Odredi 42, Skopje", "billing_address": None, "notes": None, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _client_id(2), "name": "Ana Stojanovic", "email": "ana.stojanovic@example.com", "phone": "+389 71 234 567", "address": "Ul. Makedonija 15, Bitola", "billing_address": "Ul. Makedonija 15, Bitola", "notes": "Preferred contact by email", "is_active": True, "tenant_id": TENANT_ID},
    {"id": _client_id(3), "name": "Green Valley Properties", "email": "office@greenvalley.mk", "phone": "+389 72 345 678", "address": "Bul. Kliment Ohridski 8, Ohrid", "billing_address": "PO Box 220, Ohrid", "notes": "Property management company", "is_active": True, "tenant_id": TENANT_ID},
    {"id": _client_id(4), "name": "Stefan Dimitrov", "email": "stefan.d@example.com", "phone": "+389 73 456 789", "address": "Ul. 11 Oktomvri 3, Prilep", "billing_address": None, "notes": None, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _client_id(5), "name": "City Living DOO", "email": "info@cityliving.mk", "phone": "+389 74 567 890", "address": "Bul. Jane Sandanski 100, Skopje", "billing_address": "Bul. Jane Sandanski 100, Skopje", "notes": "Corporate client — monthly billing", "is_active": True, "tenant_id": TENANT_ID},
    {"id": _client_id(6), "name": "Elena Trajkovska", "email": "elena.t@example.com", "phone": "+389 75 678 901", "address": "Ul. Nikola Karev 22, Veles", "billing_address": None, "notes": None, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _client_id(7), "name": "Horizon Real Estate", "email": "contact@horizon-re.mk", "phone": "+389 76 789 012", "address": "Ul. Vasil Glavinov 5, Skopje", "billing_address": "Ul. Vasil Glavinov 5, Skopje", "notes": "Large portfolio — multiple buildings", "is_active": True, "tenant_id": TENANT_ID},
    {"id": _client_id(8), "name": "Igor Nikolovski", "email": "igor.n@example.com", "phone": "+389 77 890 123", "address": "Ul. Goce Delchev 17, Kumanovo", "billing_address": None, "notes": None, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _client_id(9), "name": "Sunrise Hospitality", "email": "admin@sunrise-hotel.mk", "phone": "+389 78 901 234", "address": "Kej 13 Noemvri 1, Ohrid", "billing_address": "Kej 13 Noemvri 1, Ohrid", "notes": "Hotel and hospitality group", "is_active": True, "tenant_id": TENANT_ID},
    {"id": _client_id(10), "name": "Darko Angelov", "email": "darko.a@example.com", "phone": "+389 79 012 345", "address": "Ul. Marshal Tito 55, Strumica", "billing_address": None, "notes": None, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _client_id(11), "name": "Maja Ristovska", "email": "maja.r@example.com", "phone": "+389 70 111 222", "address": "Ul. Ilindenska 30, Skopje", "billing_address": None, "notes": "Owns two units in Tower A", "is_active": True, "tenant_id": TENANT_ID},
    {"id": _client_id(12), "name": "Viktor Georgiev", "email": "viktor.g@example.com", "phone": "+389 71 333 444", "address": "Ul. Partizanska 12, Skopje", "billing_address": None, "notes": None, "is_active": True, "tenant_id": TENANT_ID},
]

# ---------------------------------------------------------------------------
# Properties — 10 parent properties + child units
# ---------------------------------------------------------------------------
def _prop_id(n: int) -> uuid.UUID:
    return uuid.UUID(f"30000000-0000-0000-0000-{n:012d}")


def _unit_id(building: int, unit: int) -> uuid.UUID:
    return uuid.UUID(f"31000000-0000-0000-{building:04d}-{unit:012d}")


PROPERTIES = []
_UNIT_ROWS = []

# Building 1 — Residence Park Tower A, 10 units
# Building owned by Horizon Real Estate (property management company)
# Units owned by individual tenants — realistic mix
PROPERTIES.append({"id": _prop_id(1), "client_id": _client_id(7), "parent_property_id": None, "property_type": "building", "name": "Residence Park Tower A", "address": "Bul. Partizanski Odredi 42", "city": "Skopje", "notes": None, "is_active": True, "tenant_id": TENANT_ID})
_building1_unit_clients = [
    _client_id(1),   # Unit 1 — Marko Petrovski
    _client_id(1),   # Unit 2 — Marko Petrovski (owns 2)
    _client_id(2),   # Unit 3 — Ana Stojanovic
    _client_id(11),  # Unit 4 — Maja Ristovska
    _client_id(11),  # Unit 5 — Maja Ristovska (owns 2)
    _client_id(4),   # Unit 6 — Stefan Dimitrov
    _client_id(6),   # Unit 7 — Elena Trajkovska
    _client_id(12),  # Unit 8 — Viktor Georgiev
    _client_id(8),   # Unit 9 — Igor Nikolovski
    None,            # Unit 10 — vacant, no client
]
for u in range(1, 11):
    _UNIT_ROWS.append({"id": _unit_id(1, u), "client_id": _building1_unit_clients[u - 1], "parent_property_id": _prop_id(1), "property_type": "unit", "name": f"Unit {u}", "address": "Bul. Partizanski Odredi 42", "city": "Skopje", "notes": None, "is_active": u != 10, "tenant_id": TENANT_ID})

# Building 2 — Residence Park Tower B, 10 units
# Building owned by Horizon Real Estate
# Units owned by individual tenants
PROPERTIES.append({"id": _prop_id(2), "client_id": _client_id(7), "parent_property_id": None, "property_type": "building", "name": "Residence Park Tower B", "address": "Bul. Partizanski Odredi 44", "city": "Skopje", "notes": None, "is_active": True, "tenant_id": TENANT_ID})
_building2_unit_clients = [
    _client_id(2),   # Unit 1 — Ana Stojanovic
    _client_id(4),   # Unit 2 — Stefan Dimitrov
    _client_id(10),  # Unit 3 — Darko Angelov
    _client_id(10),  # Unit 4 — Darko Angelov (owns 2)
    _client_id(6),   # Unit 5 — Elena Trajkovska
    _client_id(12),  # Unit 6 — Viktor Georgiev
    _client_id(8),   # Unit 7 — Igor Nikolovski
    _client_id(8),   # Unit 8 — Igor Nikolovski (owns 2)
    None,            # Unit 9 — vacant
    None,            # Unit 10 — vacant
]
for u in range(1, 11):
    _UNIT_ROWS.append({"id": _unit_id(2, u), "client_id": _building2_unit_clients[u - 1], "parent_property_id": _prop_id(2), "property_type": "unit", "name": f"Unit {u}", "address": "Bul. Partizanski Odredi 44", "city": "Skopje", "notes": None, "is_active": u <= 8, "tenant_id": TENANT_ID})

# Building 3 — Green Valley Complex, 5 units
# Building owned by Green Valley Properties (management company)
# Units owned by individual clients
PROPERTIES.append({"id": _prop_id(3), "client_id": _client_id(3), "parent_property_id": None, "property_type": "building", "name": "Green Valley Complex", "address": "Bul. Kliment Ohridski 10", "city": "Ohrid", "notes": None, "is_active": True, "tenant_id": TENANT_ID})
_building3_unit_clients = [
    _client_id(1),   # Unit 1 — Marko Petrovski
    _client_id(4),   # Unit 2 — Stefan Dimitrov
    _client_id(6),   # Unit 3 — Elena Trajkovska
    _client_id(10),  # Unit 4 — Darko Angelov
    None,            # Unit 5 — vacant
]
for u in range(1, 6):
    _UNIT_ROWS.append({"id": _unit_id(3, u), "client_id": _building3_unit_clients[u - 1], "parent_property_id": _prop_id(3), "property_type": "unit", "name": f"Unit {u}", "address": "Bul. Kliment Ohridski 10", "city": "Ohrid", "notes": None, "is_active": True, "tenant_id": TENANT_ID})

# Building 4 — Horizon Residence, 5 units
# Building owned by Horizon Real Estate
# Units owned by individual clients
PROPERTIES.append({"id": _prop_id(4), "client_id": _client_id(7), "parent_property_id": None, "property_type": "building", "name": "Horizon Residence", "address": "Ul. Vasil Glavinov 7", "city": "Skopje", "notes": None, "is_active": True, "tenant_id": TENANT_ID})
_building4_unit_clients = [
    _client_id(2),   # Unit 1 — Ana Stojanovic
    _client_id(12),  # Unit 2 — Viktor Georgiev
    _client_id(5),   # Unit 3 — City Living DOO (corporate)
    _client_id(5),   # Unit 4 — City Living DOO (corporate, owns 2)
    _client_id(4),   # Unit 5 — Stefan Dimitrov
]
for u in range(1, 6):
    _UNIT_ROWS.append({"id": _unit_id(4, u), "client_id": _building4_unit_clients[u - 1], "parent_property_id": _prop_id(4), "property_type": "unit", "name": f"Unit {u}", "address": "Ul. Vasil Glavinov 7", "city": "Skopje", "notes": None, "is_active": True, "tenant_id": TENANT_ID})

# Building 5 — Old Town Lofts, 0 units, no client (under renovation)
PROPERTIES.append({"id": _prop_id(5), "client_id": None, "parent_property_id": None, "property_type": "building", "name": "Old Town Lofts", "address": "Ul. Samoilova 18", "city": "Bitola", "notes": "Under renovation", "is_active": True, "tenant_id": TENANT_ID})

# Building 6 — City Living HQ (office building), client 5
PROPERTIES.append({"id": _prop_id(6), "client_id": _client_id(5), "parent_property_id": None, "property_type": "building", "name": "City Living HQ", "address": "Bul. Jane Sandanski 102", "city": "Skopje", "notes": "Office building", "is_active": True, "tenant_id": TENANT_ID})

# Building 7 — Lakeside Apartments, 3 units, no building-level client
# Units owned by individuals
PROPERTIES.append({"id": _prop_id(7), "client_id": None, "parent_property_id": None, "property_type": "building", "name": "Lakeside Apartments", "address": "Kej Makedonija 5", "city": "Ohrid", "notes": None, "is_active": True, "tenant_id": TENANT_ID})
_building7_unit_clients = [
    _client_id(6),   # Unit 1 — Elena Trajkovska
    _client_id(10),  # Unit 2 — Darko Angelov
    None,            # Unit 3 — vacant
]
for u in range(1, 4):
    _UNIT_ROWS.append({"id": _unit_id(7, u), "client_id": _building7_unit_clients[u - 1], "parent_property_id": _prop_id(7), "property_type": "unit", "name": f"Unit {u}", "address": "Kej Makedonija 5", "city": "Ohrid", "notes": None, "is_active": True, "tenant_id": TENANT_ID})

# House — client 8 (Igor Nikolovski)
PROPERTIES.append({"id": _prop_id(8), "client_id": _client_id(8), "parent_property_id": None, "property_type": "house", "name": "Villa Panorama", "address": "Ul. Vodno 33", "city": "Skopje", "notes": "Detached family house", "is_active": True, "tenant_id": TENANT_ID})

# Commercial (hotel) — client 9 (Sunrise Hospitality)
# All hotel rooms belong to the same hotel owner — realistic
PROPERTIES.append({"id": _prop_id(9), "client_id": _client_id(9), "parent_property_id": None, "property_type": "commercial", "name": "Sunrise Hotel", "address": "Kej 13 Noemvri 1", "city": "Ohrid", "notes": "Hotel — 3 floors", "is_active": True, "tenant_id": TENANT_ID})

# Standalone apartment — client 4 (Stefan Dimitrov)
PROPERTIES.append({"id": _prop_id(10), "client_id": _client_id(4), "parent_property_id": None, "property_type": "apartment", "name": "Studio Central", "address": "Ul. Macedonia 22", "city": "Skopje", "notes": "Standalone studio apartment", "is_active": True, "tenant_id": TENANT_ID})

# Merge parents + children (parents first so FK constraint is satisfied)
ALL_PROPERTIES = PROPERTIES + _UNIT_ROWS

# ---------------------------------------------------------------------------
# Property-Service Type assignments
# Assigns services to parent properties; children inherit dynamically.
# ---------------------------------------------------------------------------
_pst_counter = 0


def _pst_id() -> uuid.UUID:
    global _pst_counter
    _pst_counter += 1
    return uuid.UUID(f"40000000-0000-0000-0000-{_pst_counter:012d}")


PROPERTY_SERVICE_TYPES = [
    # Building 1 — Regular + Deep cleaning
    {"id": _pst_id(), "property_id": _prop_id(1), "service_type_id": ST_REGULAR, "custom_price": None, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _pst_id(), "property_id": _prop_id(1), "service_type_id": ST_DEEP, "custom_price": None, "is_active": True, "tenant_id": TENANT_ID},
    # Building 2 — Regular + Window cleaning
    {"id": _pst_id(), "property_id": _prop_id(2), "service_type_id": ST_REGULAR, "custom_price": None, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _pst_id(), "property_id": _prop_id(2), "service_type_id": ST_WINDOW, "custom_price": None, "is_active": True, "tenant_id": TENANT_ID},
    # Building 3 — Regular + Deep + Carpet (with custom price on regular)
    {"id": _pst_id(), "property_id": _prop_id(3), "service_type_id": ST_REGULAR, "custom_price": 70.00, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _pst_id(), "property_id": _prop_id(3), "service_type_id": ST_DEEP, "custom_price": None, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _pst_id(), "property_id": _prop_id(3), "service_type_id": ST_CARPET, "custom_price": None, "is_active": True, "tenant_id": TENANT_ID},
    # Building 4 — Regular + Window
    {"id": _pst_id(), "property_id": _prop_id(4), "service_type_id": ST_REGULAR, "custom_price": None, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _pst_id(), "property_id": _prop_id(4), "service_type_id": ST_WINDOW, "custom_price": None, "is_active": True, "tenant_id": TENANT_ID},
    # Building 6 (office) — Regular + Deep
    {"id": _pst_id(), "property_id": _prop_id(6), "service_type_id": ST_REGULAR, "custom_price": 100.00, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _pst_id(), "property_id": _prop_id(6), "service_type_id": ST_DEEP, "custom_price": 200.00, "is_active": True, "tenant_id": TENANT_ID},
    # Building 7 — Regular only
    {"id": _pst_id(), "property_id": _prop_id(7), "service_type_id": ST_REGULAR, "custom_price": None, "is_active": True, "tenant_id": TENANT_ID},
    # House — Regular + Deep + Window
    {"id": _pst_id(), "property_id": _prop_id(8), "service_type_id": ST_REGULAR, "custom_price": None, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _pst_id(), "property_id": _prop_id(8), "service_type_id": ST_DEEP, "custom_price": None, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _pst_id(), "property_id": _prop_id(8), "service_type_id": ST_WINDOW, "custom_price": 45.00, "is_active": True, "tenant_id": TENANT_ID},
    # Commercial (hotel) — Regular + Deep + Carpet + Window
    {"id": _pst_id(), "property_id": _prop_id(9), "service_type_id": ST_REGULAR, "custom_price": 150.00, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _pst_id(), "property_id": _prop_id(9), "service_type_id": ST_DEEP, "custom_price": 350.00, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _pst_id(), "property_id": _prop_id(9), "service_type_id": ST_CARPET, "custom_price": 200.00, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _pst_id(), "property_id": _prop_id(9), "service_type_id": ST_WINDOW, "custom_price": 100.00, "is_active": True, "tenant_id": TENANT_ID},
    # Standalone apartment — Move-in/Move-out + Regular
    {"id": _pst_id(), "property_id": _prop_id(10), "service_type_id": ST_MOVEINOUT, "custom_price": None, "is_active": True, "tenant_id": TENANT_ID},
    {"id": _pst_id(), "property_id": _prop_id(10), "service_type_id": ST_REGULAR, "custom_price": 50.00, "is_active": True, "tenant_id": TENANT_ID},
    # Unit-level override: Building 1 Unit 1 gets custom price for Regular
    {"id": _pst_id(), "property_id": _unit_id(1, 1), "service_type_id": ST_REGULAR, "custom_price": 95.00, "is_active": True, "tenant_id": TENANT_ID},
    # Unit-level override: Building 3 Unit 2 opts out of Carpet cleaning
    {"id": _pst_id(), "property_id": _unit_id(3, 2), "service_type_id": ST_CARPET, "custom_price": None, "is_active": False, "tenant_id": TENANT_ID},
]

# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------
_inv_counter = 0


def _inv_id(n: int) -> uuid.UUID:
    return uuid.UUID(f"50000000-0000-0000-0000-{n:012d}")


def _inv_item_id() -> uuid.UUID:
    global _inv_counter
    _inv_counter += 1
    return uuid.UUID(f"51000000-0000-0000-0000-{_inv_counter:012d}")


TODAY = date(2026, 2, 22)

INVOICES = []
INVOICE_ITEMS = []

# -- Building 1 Unit 1 (Marko Petrovski) — Regular cleaning Jan 2026
#    Status: PAID (full payment received)
INVOICES.append({
    "id": _inv_id(1), "property_id": _unit_id(1, 1), "invoice_number": "INV-202602-0001",
    "status": "paid", "period_start": date(2026, 1, 1), "period_end": date(2026, 1, 31),
    "subtotal": 95.00, "discount": 0, "tax": 0, "total": 95.00,
    "issue_date": date(2026, 2, 1), "due_date": date(2026, 2, 15),
    "paid_date": date(2026, 2, 10), "notes": None, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(1), "service_type_id": ST_REGULAR,
    "description": "Regular Cleaning — January 2026", "quantity": 1, "unit_price": 95.00,
    "total": 95.00, "sort_order": 1, "tenant_id": TENANT_ID,
})

# -- Building 1 Unit 3 (Ana Stojanovic) — Regular + Deep Jan 2026
#    Status: PAID (full payment)
INVOICES.append({
    "id": _inv_id(2), "property_id": _unit_id(1, 3), "invoice_number": "INV-202602-0002",
    "status": "paid", "period_start": date(2026, 1, 1), "period_end": date(2026, 1, 31),
    "subtotal": 260.00, "discount": 10.00, "tax": 0, "total": 250.00,
    "issue_date": date(2026, 2, 1), "due_date": date(2026, 2, 15),
    "paid_date": date(2026, 2, 12), "notes": "Loyalty discount applied", "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(2), "service_type_id": ST_REGULAR,
    "description": "Regular Cleaning — January 2026", "quantity": 1, "unit_price": 80.00,
    "total": 80.00, "sort_order": 1, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(2), "service_type_id": ST_DEEP,
    "description": "Deep Cleaning — January 2026", "quantity": 1, "unit_price": 180.00,
    "total": 180.00, "sort_order": 2, "tenant_id": TENANT_ID,
})

# -- Villa Panorama (Igor Nikolovski) — Regular + Window Jan 2026
#    Status: SENT (no payment yet)
INVOICES.append({
    "id": _inv_id(3), "property_id": _prop_id(8), "invoice_number": "INV-202602-0003",
    "status": "sent", "period_start": date(2026, 1, 1), "period_end": date(2026, 1, 31),
    "subtotal": 125.00, "discount": 0, "tax": 0, "total": 125.00,
    "issue_date": date(2026, 2, 1), "due_date": date(2026, 2, 28),
    "paid_date": None, "notes": None, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(3), "service_type_id": ST_REGULAR,
    "description": "Regular Cleaning — January 2026", "quantity": 1, "unit_price": 80.00,
    "total": 80.00, "sort_order": 1, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(3), "service_type_id": ST_WINDOW,
    "description": "Window Cleaning — January 2026", "quantity": 1, "unit_price": 45.00,
    "total": 45.00, "sort_order": 2, "tenant_id": TENANT_ID,
})

# -- Sunrise Hotel (Sunrise Hospitality) — Big monthly invoice Jan 2026
#    Status: OVERDUE (sent but past due date, partial payment received)
INVOICES.append({
    "id": _inv_id(4), "property_id": _prop_id(9), "invoice_number": "INV-202601-0002",
    "status": "overdue", "period_start": date(2026, 1, 1), "period_end": date(2026, 1, 31),
    "subtotal": 800.00, "discount": 0, "tax": 0, "total": 800.00,
    "issue_date": date(2026, 1, 15), "due_date": date(2026, 2, 1),
    "paid_date": None, "notes": "Monthly hotel cleaning package", "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(4), "service_type_id": ST_REGULAR,
    "description": "Regular Cleaning x2 — January 2026", "quantity": 2, "unit_price": 150.00,
    "total": 300.00, "sort_order": 1, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(4), "service_type_id": ST_DEEP,
    "description": "Deep Cleaning — January 2026", "quantity": 1, "unit_price": 350.00,
    "total": 350.00, "sort_order": 2, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(4), "service_type_id": ST_WINDOW,
    "description": "Window Cleaning — January 2026", "quantity": 1, "unit_price": 100.00,
    "total": 100.00, "sort_order": 3, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(4), "service_type_id": ST_CARPET,
    "description": "Carpet Cleaning — half floors", "quantity": 0.50, "unit_price": 100.00,
    "total": 50.00, "sort_order": 4, "tenant_id": TENANT_ID,
})

# -- Building 3 Unit 1 (Marko Petrovski) — Regular Jan 2026
#    Status: OVERDUE (sent, past due, no payment)
INVOICES.append({
    "id": _inv_id(5), "property_id": _unit_id(3, 1), "invoice_number": "INV-202601-0004",
    "status": "overdue", "period_start": date(2026, 1, 1), "period_end": date(2026, 1, 31),
    "subtotal": 70.00, "discount": 0, "tax": 0, "total": 70.00,
    "issue_date": date(2026, 1, 20), "due_date": date(2026, 2, 5),
    "paid_date": None, "notes": None, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(5), "service_type_id": ST_REGULAR,
    "description": "Regular Cleaning — January 2026", "quantity": 1, "unit_price": 70.00,
    "total": 70.00, "sort_order": 1, "tenant_id": TENANT_ID,
})

# -- Studio Central (Stefan Dimitrov) — Move-in cleaning
#    Status: PAID (full payment)
INVOICES.append({
    "id": _inv_id(6), "property_id": _prop_id(10), "invoice_number": "INV-202601-0001",
    "status": "paid", "period_start": None, "period_end": None,
    "subtotal": 250.00, "discount": 0, "tax": 0, "total": 250.00,
    "issue_date": date(2026, 1, 10), "due_date": date(2026, 1, 25),
    "paid_date": date(2026, 1, 18), "notes": "Move-in cleaning for new tenant", "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(6), "service_type_id": ST_MOVEINOUT,
    "description": "Move-in/Move-out Cleaning", "quantity": 1, "unit_price": 250.00,
    "total": 250.00, "sort_order": 1, "tenant_id": TENANT_ID,
})

# -- Building 4 Unit 3 (City Living DOO) — Regular Jan 2026
#    Status: DRAFT (not yet sent)
INVOICES.append({
    "id": _inv_id(7), "property_id": _unit_id(4, 3), "invoice_number": "INV-202602-0006",
    "status": "draft", "period_start": date(2026, 1, 1), "period_end": date(2026, 1, 31),
    "subtotal": 80.00, "discount": 0, "tax": 0, "total": 80.00,
    "issue_date": date(2026, 2, 5), "due_date": date(2026, 2, 20),
    "paid_date": None, "notes": None, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(7), "service_type_id": ST_REGULAR,
    "description": "Regular Cleaning — January 2026", "quantity": 1, "unit_price": 80.00,
    "total": 80.00, "sort_order": 1, "tenant_id": TENANT_ID,
})

# -- Building 2 Unit 1 (Ana Stojanovic) — Regular + Window Jan 2026
#    Status: SENT (partial payment received)
INVOICES.append({
    "id": _inv_id(8), "property_id": _unit_id(2, 1), "invoice_number": "INV-202602-0004",
    "status": "sent", "period_start": date(2026, 1, 1), "period_end": date(2026, 1, 31),
    "subtotal": 140.00, "discount": 0, "tax": 0, "total": 140.00,
    "issue_date": date(2026, 2, 1), "due_date": date(2026, 2, 28),
    "paid_date": None, "notes": None, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(8), "service_type_id": ST_REGULAR,
    "description": "Regular Cleaning — January 2026", "quantity": 1, "unit_price": 80.00,
    "total": 80.00, "sort_order": 1, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(8), "service_type_id": ST_WINDOW,
    "description": "Window Cleaning — January 2026", "quantity": 1, "unit_price": 60.00,
    "total": 60.00, "sort_order": 2, "tenant_id": TENANT_ID,
})

# -- Building 1 Unit 4 (Maja Ristovska) — Regular + Deep Feb 2026
#    Status: DRAFT (new invoice being prepared)
INVOICES.append({
    "id": _inv_id(9), "property_id": _unit_id(1, 4), "invoice_number": "INV-202602-0008",
    "status": "draft", "period_start": date(2026, 2, 1), "period_end": date(2026, 2, 28),
    "subtotal": 260.00, "discount": 0, "tax": 0, "total": 260.00,
    "issue_date": date(2026, 2, 20), "due_date": date(2026, 3, 10),
    "paid_date": None, "notes": None, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(9), "service_type_id": ST_REGULAR,
    "description": "Regular Cleaning — February 2026", "quantity": 1, "unit_price": 80.00,
    "total": 80.00, "sort_order": 1, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(9), "service_type_id": ST_DEEP,
    "description": "Deep Cleaning — February 2026", "quantity": 1, "unit_price": 180.00,
    "total": 180.00, "sort_order": 2, "tenant_id": TENANT_ID,
})

# -- City Living HQ (City Living DOO) — Regular + Deep Jan 2026
#    Status: CANCELLED (client cancelled the service)
INVOICES.append({
    "id": _inv_id(10), "property_id": _prop_id(6), "invoice_number": "INV-202601-0003",
    "status": "cancelled", "period_start": date(2026, 1, 1), "period_end": date(2026, 1, 31),
    "subtotal": 300.00, "discount": 0, "tax": 0, "total": 300.00,
    "issue_date": date(2026, 1, 15), "due_date": date(2026, 2, 1),
    "paid_date": None, "notes": "Cancelled — office closed for remodeling", "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(10), "service_type_id": ST_REGULAR,
    "description": "Regular Cleaning — January 2026", "quantity": 1, "unit_price": 100.00,
    "total": 100.00, "sort_order": 1, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(10), "service_type_id": ST_DEEP,
    "description": "Deep Cleaning — January 2026", "quantity": 1, "unit_price": 200.00,
    "total": 200.00, "sort_order": 2, "tenant_id": TENANT_ID,
})

# -- Sunrise Hotel — Feb 2026 (sent, not yet due)
#    Status: SENT
INVOICES.append({
    "id": _inv_id(11), "property_id": _prop_id(9), "invoice_number": "INV-202602-0007",
    "status": "sent", "period_start": date(2026, 2, 1), "period_end": date(2026, 2, 28),
    "subtotal": 500.00, "discount": 50.00, "tax": 0, "total": 450.00,
    "issue_date": date(2026, 2, 15), "due_date": date(2026, 3, 1),
    "paid_date": None, "notes": "February package — off-season discount", "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(11), "service_type_id": ST_REGULAR,
    "description": "Regular Cleaning x2 — February 2026", "quantity": 2, "unit_price": 150.00,
    "total": 300.00, "sort_order": 1, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(11), "service_type_id": ST_CARPET,
    "description": "Carpet Cleaning — February 2026", "quantity": 1, "unit_price": 200.00,
    "total": 200.00, "sort_order": 2, "tenant_id": TENANT_ID,
})

# -- Building 1 Unit 6 (Stefan Dimitrov) — Regular Jan 2026
#    Status: PAID (paid in two installments)
INVOICES.append({
    "id": _inv_id(12), "property_id": _unit_id(1, 6), "invoice_number": "INV-202602-0005",
    "status": "paid", "period_start": date(2026, 1, 1), "period_end": date(2026, 1, 31),
    "subtotal": 80.00, "discount": 0, "tax": 0, "total": 80.00,
    "issue_date": date(2026, 2, 1), "due_date": date(2026, 2, 15),
    "paid_date": date(2026, 2, 14), "notes": None, "tenant_id": TENANT_ID,
})
INVOICE_ITEMS.append({
    "id": _inv_item_id(), "invoice_id": _inv_id(12), "service_type_id": ST_REGULAR,
    "description": "Regular Cleaning — January 2026", "quantity": 1, "unit_price": 80.00,
    "total": 80.00, "sort_order": 1, "tenant_id": TENANT_ID,
})

# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------
_pay_counter = 0


def _pay_id() -> uuid.UUID:
    global _pay_counter
    _pay_counter += 1
    return uuid.UUID(f"60000000-0000-0000-0000-{_pay_counter:012d}")


PAYMENTS = [
    # INV-001: Full payment — 95.00 (PAID)
    {"id": _pay_id(), "invoice_id": _inv_id(1), "amount": 95.00, "payment_date": date(2026, 2, 10),
     "payment_method": "bank_transfer", "reference": "BT-20260210-001", "notes": None, "tenant_id": TENANT_ID},

    # INV-002: Full payment — 250.00 (PAID)
    {"id": _pay_id(), "invoice_id": _inv_id(2), "amount": 250.00, "payment_date": date(2026, 2, 12),
     "payment_method": "bank_transfer", "reference": "BT-20260212-001", "notes": None, "tenant_id": TENANT_ID},

    # INV-004: Partial payment — 300.00 of 800.00 (OVERDUE, still 500 remaining)
    {"id": _pay_id(), "invoice_id": _inv_id(4), "amount": 300.00, "payment_date": date(2026, 1, 28),
     "payment_method": "bank_transfer", "reference": "BT-20260128-001", "notes": "Partial — first installment", "tenant_id": TENANT_ID},

    # INV-006: Full payment — 250.00 (PAID)
    {"id": _pay_id(), "invoice_id": _inv_id(6), "amount": 250.00, "payment_date": date(2026, 1, 18),
     "payment_method": "cash", "reference": None, "notes": "Cash on completion", "tenant_id": TENANT_ID},

    # INV-008: Partial payment — 80.00 of 140.00 (SENT, 60 remaining)
    {"id": _pay_id(), "invoice_id": _inv_id(8), "amount": 80.00, "payment_date": date(2026, 2, 18),
     "payment_method": "card", "reference": "CARD-4521", "notes": "Partial — cleaning portion", "tenant_id": TENANT_ID},

    # INV-012: Paid in two installments (PAID)
    {"id": _pay_id(), "invoice_id": _inv_id(12), "amount": 40.00, "payment_date": date(2026, 2, 8),
     "payment_method": "cash", "reference": None, "notes": "First half", "tenant_id": TENANT_ID},
    {"id": _pay_id(), "invoice_id": _inv_id(12), "amount": 40.00, "payment_date": date(2026, 2, 14),
     "payment_method": "cash", "reference": None, "notes": "Second half", "tenant_id": TENANT_ID},
]


# ---------------------------------------------------------------------------
# Insert helpers
# ---------------------------------------------------------------------------
async def _insert_rows(session: AsyncSession, table: str, rows: list[dict]) -> int:
    """Insert rows using raw SQL. Returns count inserted."""
    if not rows:
        return 0
    cols = list(rows[0].keys())
    col_list = ", ".join(cols)
    param_list = ", ".join(f":{c}" for c in cols)
    stmt = text(f"INSERT INTO {table} ({col_list}) VALUES ({param_list})")
    for row in rows:
        await session.execute(stmt, row)
    return len(rows)


async def seed() -> None:
    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(text("SELECT count(*) FROM service_types"))
        if result.scalar() > 0:
            print("Database already has service types — skipping seed.")
            return

        print("Seeding service types...")
        await _insert_rows(session, "service_types", SERVICE_TYPES)

        print("Seeding checklist items...")
        await _insert_rows(session, "checklist_items", CHECKLIST_ITEMS)

        print("Seeding clients...")
        await _insert_rows(session, "clients", CLIENTS)

        print("Seeding properties...")
        await _insert_rows(session, "properties", ALL_PROPERTIES)

        print("Seeding property-service assignments...")
        await _insert_rows(session, "property_service_types", PROPERTY_SERVICE_TYPES)

        print("Seeding invoices...")
        await _insert_rows(session, "invoices", INVOICES)

        print("Seeding invoice items...")
        await _insert_rows(session, "invoice_items", INVOICE_ITEMS)

        print("Seeding payments...")
        await _insert_rows(session, "payments", PAYMENTS)

        await session.commit()

        print(
            f"Done! Inserted {len(SERVICE_TYPES)} service types, "
            f"{len(CHECKLIST_ITEMS)} checklist items, "
            f"{len(CLIENTS)} clients, "
            f"{len(ALL_PROPERTIES)} properties, "
            f"{len(PROPERTY_SERVICE_TYPES)} property-service assignments, "
            f"{len(INVOICES)} invoices, "
            f"{len(INVOICE_ITEMS)} invoice items, "
            f"{len(PAYMENTS)} payments."
        )


if __name__ == "__main__":
    asyncio.run(seed())
