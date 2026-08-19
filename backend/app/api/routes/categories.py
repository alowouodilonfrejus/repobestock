from fastapi import APIRouter

from app.api.deps import ActiveUser, DbSession
from app.crud import category as crud_category
from app.schemas.category import CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def read_categories(db: DbSession, current_user: ActiveUser):
    return await crud_category.list_categories(db)
