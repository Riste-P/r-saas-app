from sqlalchemy import Select

from app.core.dependencies import is_superadmin
from app.models.user import User


def tenant_filter(query: Select, user: User, tenant_id_column) -> Select:
    """Apply tenant isolation to a query. SuperAdmin bypasses the filter."""
    if is_superadmin(user):
        return query
    return query.where(tenant_id_column == user.tenant_id)
