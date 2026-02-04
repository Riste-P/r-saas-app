from fastapi import Query


class PaginationParams:
    """Reusable dependency for offset/limit pagination."""

    def __init__(
        self,
        offset: int = Query(0, ge=0, description="Number of items to skip"),
        limit: int = Query(50, ge=1, le=200, description="Max items to return"),
    ):
        self.offset = offset
        self.limit = limit
