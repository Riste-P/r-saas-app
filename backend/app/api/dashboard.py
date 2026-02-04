import random

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def stats(user: User = Depends(get_current_user)):
    return {
        "tenant": user.tenant.name,
        "total_users": random.randint(10, 500),
        "active_users": random.randint(5, 200),
        "revenue": round(random.uniform(1000, 50000), 2),
        "growth": round(random.uniform(-5, 25), 1),
    }
