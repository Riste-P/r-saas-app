from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.dto.auth import LoginRequest
from app.dto.invoice import CreateInvoiceRequest, InvoiceItemRequest, UpdateInvoiceRequest
from app.dto.payment import CreatePaymentRequest
from app.dto.property import ServiceBadgeItem, _compute_service_badges
from app.dto.property_service_type import (
    AssignServiceRequest,
    EffectiveServiceResponse,
    PropertyServiceTypeResponse,
    UpdatePropertyServiceRequest,
)
from app.dto.user import CreateUserRequest, UpdateUserRequest
from app.services.invoice_service import _calc_totals


class TestLoginRequest:
    def test_valid(self):
        req = LoginRequest(email="user@example.com", password="secret")
        assert req.email == "user@example.com"

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="not-an-email", password="secret")

    def test_missing_password_rejected(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com")


class TestCreateUserRequest:
    def test_defaults(self):
        req = CreateUserRequest(email="a@b.com", password="pw")
        assert req.role_id == 3
        assert req.tenant_id is None

    def test_with_tenant(self):
        tid = uuid4()
        req = CreateUserRequest(email="a@b.com", password="pw", tenant_id=tid)
        assert req.tenant_id == tid

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            CreateUserRequest(email="bad", password="pw")


class TestUpdateUserRequest:
    def test_all_optional(self):
        req = UpdateUserRequest()
        assert req.role_id is None
        assert req.is_active is None

    def test_partial_update(self):
        req = UpdateUserRequest(is_active=False)
        assert req.is_active is False
        assert req.role_id is None


# ---------------------------------------------------------------------------
# Fakes for _compute_service_badges (avoid importing real ORM models)
# ---------------------------------------------------------------------------

@dataclass
class _FakeServiceType:
    name: str
    base_price: Decimal


@dataclass
class _FakeAssignment:
    service_type_id: UUID
    service_type: _FakeServiceType
    custom_price: Decimal | None = None
    is_active: bool = True
    deleted_at: object = None


@dataclass
class _FakeProperty:
    parent_property_id: UUID | None = None
    service_assignments: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# _compute_service_badges unit tests
# ---------------------------------------------------------------------------

class TestComputeServiceBadges:
    def test_direct_assignments_no_parent(self):
        st_id = uuid4()
        st = _FakeServiceType(name="Cleaning", base_price=Decimal("50"))
        prop = _FakeProperty(
            service_assignments=[_FakeAssignment(service_type_id=st_id, service_type=st)]
        )
        badges = _compute_service_badges(prop)
        assert len(badges) == 1
        assert badges[0].service_type_name == "Cleaning"
        assert badges[0].effective_price == Decimal("50")
        assert badges[0].is_active is True

    def test_direct_with_custom_price(self):
        st_id = uuid4()
        st = _FakeServiceType(name="Deep Clean", base_price=Decimal("100"))
        prop = _FakeProperty(
            service_assignments=[
                _FakeAssignment(service_type_id=st_id, service_type=st, custom_price=Decimal("75"))
            ]
        )
        badges = _compute_service_badges(prop)
        assert badges[0].effective_price == Decimal("75")

    def test_skips_soft_deleted(self):
        st_id = uuid4()
        st = _FakeServiceType(name="Deleted Svc", base_price=Decimal("50"))
        prop = _FakeProperty(
            service_assignments=[
                _FakeAssignment(service_type_id=st_id, service_type=st, deleted_at="2026-01-01")
            ]
        )
        badges = _compute_service_badges(prop)
        assert len(badges) == 0

    def test_child_inherits_from_parent(self):
        st_id = uuid4()
        st = _FakeServiceType(name="Inherited Svc", base_price=Decimal("80"))
        parent_assignments = [
            _FakeAssignment(service_type_id=st_id, service_type=st)
        ]
        child = _FakeProperty(service_assignments=[])
        badges = _compute_service_badges(child, parent_assignments=parent_assignments)
        assert len(badges) == 1
        assert badges[0].effective_price == Decimal("80")
        assert badges[0].is_active is True

    def test_child_override_price(self):
        st_id = uuid4()
        st = _FakeServiceType(name="Override Svc", base_price=Decimal("100"))
        parent_assignments = [
            _FakeAssignment(service_type_id=st_id, service_type=st)
        ]
        child = _FakeProperty(
            service_assignments=[
                _FakeAssignment(service_type_id=st_id, service_type=st, custom_price=Decimal("40"))
            ]
        )
        badges = _compute_service_badges(child, parent_assignments=parent_assignments)
        assert len(badges) == 1
        assert badges[0].effective_price == Decimal("40")

    def test_child_opt_out(self):
        st_id = uuid4()
        st = _FakeServiceType(name="OptOut Svc", base_price=Decimal("50"))
        parent_assignments = [
            _FakeAssignment(service_type_id=st_id, service_type=st)
        ]
        child = _FakeProperty(
            service_assignments=[
                _FakeAssignment(service_type_id=st_id, service_type=st, is_active=False)
            ]
        )
        badges = _compute_service_badges(child, parent_assignments=parent_assignments)
        assert len(badges) == 1
        assert badges[0].is_active is False

    def test_child_own_service_not_from_parent(self):
        """Child has a direct service not assigned to parent."""
        parent_st_id = uuid4()
        child_st_id = uuid4()
        pst = _FakeServiceType(name="Parent Svc", base_price=Decimal("50"))
        cst = _FakeServiceType(name="Child Svc", base_price=Decimal("30"))
        parent_assignments = [
            _FakeAssignment(service_type_id=parent_st_id, service_type=pst)
        ]
        child = _FakeProperty(
            service_assignments=[
                _FakeAssignment(service_type_id=child_st_id, service_type=cst)
            ]
        )
        badges = _compute_service_badges(child, parent_assignments=parent_assignments)
        assert len(badges) == 2
        names = {b.service_type_name for b in badges}
        assert names == {"Parent Svc", "Child Svc"}

    def test_parent_custom_price_inherited_to_child(self):
        """Parent has custom_price → child inherits that price."""
        st_id = uuid4()
        st = _FakeServiceType(name="Custom Inherited", base_price=Decimal("100"))
        parent_assignments = [
            _FakeAssignment(service_type_id=st_id, service_type=st, custom_price=Decimal("70"))
        ]
        child = _FakeProperty(service_assignments=[])
        badges = _compute_service_badges(child, parent_assignments=parent_assignments)
        assert badges[0].effective_price == Decimal("70")

    def test_parent_inactive_service_excluded(self):
        """Parent's inactive service is NOT inherited by child."""
        st_id = uuid4()
        st = _FakeServiceType(name="Inactive Parent", base_price=Decimal("50"))
        parent_assignments = [
            _FakeAssignment(service_type_id=st_id, service_type=st, is_active=False)
        ]
        child = _FakeProperty(service_assignments=[])
        badges = _compute_service_badges(child, parent_assignments=parent_assignments)
        assert len(badges) == 0


# ---------------------------------------------------------------------------
# PropertyServiceTypeResponse.from_entity effective_price computation
# ---------------------------------------------------------------------------

class TestPropertyServiceTypeResponseFromEntity:
    def test_effective_price_uses_custom_price(self):
        st_id = uuid4()
        prop_id = uuid4()

        @dataclass
        class _FakePST:
            id: UUID = field(default_factory=uuid4)
            property_id: UUID = field(default_factory=uuid4)
            service_type_id: UUID = field(default_factory=uuid4)
            service_type: _FakeServiceType = field(default_factory=lambda: _FakeServiceType("Svc", Decimal("100")))
            custom_price: Decimal | None = Decimal("60")
            is_active: bool = True
            created_at: str = "2026-01-01T00:00:00"
            updated_at: str | None = None

        pst = _FakePST()
        resp = PropertyServiceTypeResponse.from_entity(pst)
        assert resp.effective_price == Decimal("60")

    def test_effective_price_falls_back_to_base(self):
        @dataclass
        class _FakePST:
            id: UUID = field(default_factory=uuid4)
            property_id: UUID = field(default_factory=uuid4)
            service_type_id: UUID = field(default_factory=uuid4)
            service_type: _FakeServiceType = field(default_factory=lambda: _FakeServiceType("Svc", Decimal("100")))
            custom_price: Decimal | None = None
            is_active: bool = True
            created_at: str = "2026-01-01T00:00:00"
            updated_at: str | None = None

        pst = _FakePST()
        resp = PropertyServiceTypeResponse.from_entity(pst)
        assert resp.effective_price == Decimal("100")


# ---------------------------------------------------------------------------
# _calc_totals unit tests
# ---------------------------------------------------------------------------

class TestCalcTotals:
    def test_basic(self):
        items = [
            {"total": Decimal("100")},
            {"total": Decimal("50")},
        ]
        subtotal, total = _calc_totals(items, Decimal("0"), Decimal("0"))
        assert subtotal == Decimal("150")
        assert total == Decimal("150")

    def test_with_discount_and_tax(self):
        items = [{"total": Decimal("200")}]
        subtotal, total = _calc_totals(items, Decimal("30"), Decimal("10"))
        assert subtotal == Decimal("200")
        assert total == Decimal("180")  # 200 - 30 + 10

    def test_empty_items(self):
        subtotal, total = _calc_totals([], Decimal("0"), Decimal("0"))
        assert subtotal == Decimal("0")
        assert total == Decimal("0")

    def test_discount_larger_than_subtotal(self):
        items = [{"total": Decimal("50")}]
        subtotal, total = _calc_totals(items, Decimal("100"), Decimal("0"))
        assert subtotal == Decimal("50")
        assert total == Decimal("-50")  # No clamping — business rule


# ---------------------------------------------------------------------------
# Invoice DTO validation
# ---------------------------------------------------------------------------

class TestCreateInvoiceRequest:
    def test_valid(self):
        req = CreateInvoiceRequest(
            property_id=uuid4(),
            issue_date="2026-02-01",
            due_date="2026-03-01",
            items=[InvoiceItemRequest(description="Test", unit_price=Decimal("50"))],
        )
        assert req.discount == Decimal("0")
        assert req.tax == Decimal("0")
        assert len(req.items) == 1

    def test_defaults(self):
        req = CreateInvoiceRequest(
            property_id=uuid4(),
            issue_date="2026-02-01",
            due_date="2026-03-01",
        )
        assert req.items == []
        assert req.period_start is None
        assert req.notes is None


class TestUpdateInvoiceRequest:
    def test_all_optional(self):
        req = UpdateInvoiceRequest()
        assert req.status is None
        assert req.discount is None

    def test_paid_date_in_model_fields_set(self):
        req = UpdateInvoiceRequest(paid_date=None)
        assert "paid_date" in req.model_fields_set

    def test_paid_date_not_in_fields_set_when_omitted(self):
        req = UpdateInvoiceRequest(status="sent")
        assert "paid_date" not in req.model_fields_set


# ---------------------------------------------------------------------------
# Payment DTO validation
# ---------------------------------------------------------------------------

class TestCreatePaymentRequest:
    def test_valid(self):
        req = CreatePaymentRequest(
            invoice_id=uuid4(),
            amount=Decimal("50"),
            payment_date="2026-02-15",
            payment_method="bank_transfer",
        )
        assert req.reference is None
        assert req.notes is None

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            CreatePaymentRequest(invoice_id=uuid4())


# ---------------------------------------------------------------------------
# AssignServiceRequest / UpdatePropertyServiceRequest DTO validation
# ---------------------------------------------------------------------------

class TestAssignServiceRequest:
    def test_valid(self):
        req = AssignServiceRequest(
            property_id=uuid4(),
            service_type_id=uuid4(),
        )
        assert req.custom_price is None
        assert req.is_active is True

    def test_with_custom_price_and_inactive(self):
        req = AssignServiceRequest(
            property_id=uuid4(),
            service_type_id=uuid4(),
            custom_price=Decimal("30"),
            is_active=False,
        )
        assert req.custom_price == Decimal("30")
        assert req.is_active is False


class TestUpdatePropertyServiceRequest:
    def test_all_optional(self):
        req = UpdatePropertyServiceRequest()
        assert req.custom_price is None
        assert req.is_active is None

    def test_custom_price_in_fields_set_when_null(self):
        req = UpdatePropertyServiceRequest(custom_price=None)
        assert "custom_price" in req.model_fields_set
