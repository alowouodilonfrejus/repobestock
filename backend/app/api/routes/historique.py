from fastapi import APIRouter, Query

from app.api.deps import ActiveUser, DbSession
from app.crud import historique as crud_historique
from app.schemas.historique import HistoriqueRead

router = APIRouter(prefix="/historique", tags=["historique"])


@router.get("", response_model=list[HistoriqueRead])
async def read_historique(
    db: DbSession,
    current_user: ActiveUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
):
    return await crud_historique.list_historique(db, skip=skip, limit=limit)
