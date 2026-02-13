"""
Seed script — populates the database with sample data.

Run inside the backend container:
    docker-compose exec backend python -m scripts.seed

Idempotent: skips inserts if data already exists (checks service_types table).
"""

import asyncio
import uuid

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
# Clients (10)
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
]

# ---------------------------------------------------------------------------
# Properties — 10 parent properties + child apartments
# ---------------------------------------------------------------------------
def _prop_id(n: int) -> uuid.UUID:
    return uuid.UUID(f"30000000-0000-0000-0000-{n:012d}")


def _apt_id(building: int, unit: int) -> uuid.UUID:
    return uuid.UUID(f"31000000-0000-0000-{building:04d}-{unit:012d}")


PROPERTIES = []
_APT_ROWS = []

# Building 1 — 10 apartments, client 1
PROPERTIES.append({"id": _prop_id(1), "client_id": _client_id(1), "parent_property_id": None, "property_type": "building", "name": "Residence Park Tower A", "address": "Bul. Partizanski Odredi 42", "city": "Skopje", "notes": None, "is_active": True, "tenant_id": TENANT_ID})
for u in range(1, 11):
    _APT_ROWS.append({"id": _apt_id(1, u), "client_id": _client_id(1), "parent_property_id": _prop_id(1), "property_type": "apartment", "name": f"Apt {u}", "address": "Bul. Partizanski Odredi 42", "city": "Skopje", "notes": None, "is_active": True, "tenant_id": TENANT_ID})

# Building 2 — 10 apartments, client 2
PROPERTIES.append({"id": _prop_id(2), "client_id": _client_id(2), "parent_property_id": None, "property_type": "building", "name": "Residence Park Tower B", "address": "Bul. Partizanski Odredi 44", "city": "Skopje", "notes": None, "is_active": True, "tenant_id": TENANT_ID})
for u in range(1, 11):
    _APT_ROWS.append({"id": _apt_id(2, u), "client_id": _client_id(2), "parent_property_id": _prop_id(2), "property_type": "apartment", "name": f"Apt {u}", "address": "Bul. Partizanski Odredi 44", "city": "Skopje", "notes": None, "is_active": True, "tenant_id": TENANT_ID})

# Building 3 — 5 apartments, client 3
PROPERTIES.append({"id": _prop_id(3), "client_id": _client_id(3), "parent_property_id": None, "property_type": "building", "name": "Green Valley Complex", "address": "Bul. Kliment Ohridski 10", "city": "Ohrid", "notes": None, "is_active": True, "tenant_id": TENANT_ID})
for u in range(1, 6):
    _APT_ROWS.append({"id": _apt_id(3, u), "client_id": _client_id(3), "parent_property_id": _prop_id(3), "property_type": "apartment", "name": f"Apt {u}", "address": "Bul. Kliment Ohridski 10", "city": "Ohrid", "notes": None, "is_active": True, "tenant_id": TENANT_ID})

# Building 4 — 5 apartments, client 7
PROPERTIES.append({"id": _prop_id(4), "client_id": _client_id(7), "parent_property_id": None, "property_type": "building", "name": "Horizon Residence", "address": "Ul. Vasil Glavinov 7", "city": "Skopje", "notes": None, "is_active": True, "tenant_id": TENANT_ID})
for u in range(1, 6):
    _APT_ROWS.append({"id": _apt_id(4, u), "client_id": _client_id(7), "parent_property_id": _prop_id(4), "property_type": "apartment", "name": f"Apt {u}", "address": "Ul. Vasil Glavinov 7", "city": "Skopje", "notes": None, "is_active": True, "tenant_id": TENANT_ID})

# Building 5 — 0 apartments, no client
PROPERTIES.append({"id": _prop_id(5), "client_id": None, "parent_property_id": None, "property_type": "building", "name": "Old Town Lofts", "address": "Ul. Samoilova 18", "city": "Bitola", "notes": "Under renovation", "is_active": True, "tenant_id": TENANT_ID})

# Building 6 — 0 apartments, client 5
PROPERTIES.append({"id": _prop_id(6), "client_id": _client_id(5), "parent_property_id": None, "property_type": "building", "name": "City Living HQ", "address": "Bul. Jane Sandanski 102", "city": "Skopje", "notes": "Office building", "is_active": True, "tenant_id": TENANT_ID})

# Building 7 — 3 apartments, no client
PROPERTIES.append({"id": _prop_id(7), "client_id": None, "parent_property_id": None, "property_type": "building", "name": "Lakeside Apartments", "address": "Kej Makedonija 5", "city": "Ohrid", "notes": None, "is_active": True, "tenant_id": TENANT_ID})
for u in range(1, 4):
    _APT_ROWS.append({"id": _apt_id(7, u), "client_id": None, "parent_property_id": _prop_id(7), "property_type": "apartment", "name": f"Apt {u}", "address": "Kej Makedonija 5", "city": "Ohrid", "notes": None, "is_active": True, "tenant_id": TENANT_ID})

# House — no client
PROPERTIES.append({"id": _prop_id(8), "client_id": None, "parent_property_id": None, "property_type": "house", "name": "Villa Panorama", "address": "Ul. Vodno 33", "city": "Skopje", "notes": "Detached family house", "is_active": True, "tenant_id": TENANT_ID})

# Commercial — client 9
PROPERTIES.append({"id": _prop_id(9), "client_id": _client_id(9), "parent_property_id": None, "property_type": "commercial", "name": "Sunrise Hotel", "address": "Kej 13 Noemvri 1", "city": "Ohrid", "notes": "Hotel — 3 floors", "is_active": True, "tenant_id": TENANT_ID})

# Standalone apartment — no parent, no client
PROPERTIES.append({"id": _prop_id(10), "client_id": None, "parent_property_id": None, "property_type": "apartment", "name": "Studio Central", "address": "Ul. Macedonia 22", "city": "Skopje", "notes": "Standalone studio apartment", "is_active": True, "tenant_id": TENANT_ID})

# Merge parents + children (parents first so FK constraint is satisfied)
ALL_PROPERTIES = PROPERTIES + _APT_ROWS


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

        await session.commit()

        print(
            f"Done! Inserted {len(SERVICE_TYPES)} service types, "
            f"{len(CHECKLIST_ITEMS)} checklist items, "
            f"{len(CLIENTS)} clients, "
            f"{len(ALL_PROPERTIES)} properties."
        )


if __name__ == "__main__":
    asyncio.run(seed())
