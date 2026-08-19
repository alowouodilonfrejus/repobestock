from fastapi import APIRouter

from app.api.deps import ActiveUser, DbSession
from app.crud import statut as crud_statut
from app.schemas.statut import StatutRead

router = APIRouter(prefix="/statuts", tags=["statuts"])


@router.get("", response_model=list[StatutRead])
async def read_statuts(db: DbSession, current_user: ActiveUser):
    return await crud_statut.list_statuts(db)
