from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.database import get_db
from app.database.models.user import User
from app.dto.property_service_type import (
    AssignServiceRequest,
    BulkAssignServicesRequest,
    EffectiveServiceResponse,
    PropertyServiceTypeResponse,
    UpdatePropertyServiceRequest,
)
from app.services import property_service_type_service

router = APIRouter(prefix="/property-service-types", tags=["property-service-types"])


@router.get("", response_model=list[PropertyServiceTypeResponse])
async def list_assignments(
    property_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await property_service_type_service.list_assignments(
        property_id, user, db
    )
    return [PropertyServiceTypeResponse.from_entity(pst) for pst in items]


@router.get("/effective", response_model=list[EffectiveServiceResponse])
async def get_effective_services(
    property_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await property_service_type_service.get_effective_services(
        property_id, user, db
    )


@router.post("", response_model=PropertyServiceTypeResponse, status_code=status.HTTP_201_CREATED)
async def assign_service(
    body: AssignServiceRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    pst = await property_service_type_service.assign_service(body, user, db)
    return PropertyServiceTypeResponse.from_entity(pst)


@router.post("/bulk", response_model=list[PropertyServiceTypeResponse], status_code=status.HTTP_201_CREATED)
async def bulk_assign_services(
    body: BulkAssignServicesRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    items = await property_service_type_service.bulk_assign_services(body, user, db)
    return [PropertyServiceTypeResponse.from_entity(pst) for pst in items]


@router.patch("/{assignment_id}", response_model=PropertyServiceTypeResponse)
async def update_assignment(
    assignment_id: UUID,
    body: UpdatePropertyServiceRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    pst = await property_service_type_service.update_assignment(
        assignment_id, body, user, db
    )
    return PropertyServiceTypeResponse.from_entity(pst)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_assignment(
    assignment_id: UUID,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    await property_service_type_service.remove_assignment(assignment_id, user, db)
