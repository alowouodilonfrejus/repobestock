from fastapi import APIRouter

from app.api.deps import DbSession, PermDep
from app.crud import statut as crud_statut
from app.schemas.statut import StatutRead

router = APIRouter(prefix="/statuts", tags=["statuts"])


@router.get("", response_model=list[StatutRead])
async def read_statuts(db: DbSession, current_user: PermDep("referentiels:read")):
    return await crud_statut.list_statuts(db)
