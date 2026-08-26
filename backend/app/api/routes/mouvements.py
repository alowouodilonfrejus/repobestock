from fastapi import APIRouter, Query

from app.api.deps import DbSession, PermDep
from app.crud import mouvements as crud_mouvements
from app.schemas.mouvement import MouvementList

router = APIRouter(prefix="/mouvements", tags=["mouvements"])


@router.get("", response_model=MouvementList)
async def read_mouvements(
    db: DbSession,
    current_user: PermDep("stock:read"),
    equipement_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Timeline globale (ou par materiel) des mouvements de stock.

    Lecture seule : un mouvement n'est jamais modifie ni supprime.
    """
    items, total = await crud_mouvements.list_mouvements(
        db, skip=skip, limit=limit, equipement_id=equipement_id
    )
    return MouvementList(items=items, total=total, limit=limit, skip=skip)
