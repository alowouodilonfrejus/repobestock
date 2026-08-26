from fastapi import APIRouter, Query, Request, status

from app.api.deps import ActiveUser, DbSession, PermDep, get_client_ip
from app.models.user import UserRole
from app.crud import equipement as crud_equipement
from app.crud import historique as crud_historique
from app.schemas.equipement import (
    EquipementCreate,
    EquipementList,
    EquipementRead,
    EquipementStats,
    EquipementUpdate,
)
from app.schemas.historique import HistoriqueRead
from app.services import equipement as equipement_service

GestionDep = PermDep("stock:write")

router = APIRouter(prefix="/equipements", tags=["equipements"])


@router.get("", response_model=EquipementList)
async def read_equipements(
    db: DbSession,
    current_user: PermDep("stock:read"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    categorie_id: int | None = Query(None),
):
    items, total = await crud_equipement.list_equipements(
        db, skip=skip, limit=limit, categorie_id=categorie_id
    )
    return EquipementList(items=items, total=total, limit=limit, skip=skip)


@router.get("/stats", response_model=EquipementStats)
async def read_equipement_stats(
    db: DbSession,
    current_user: PermDep("stock:read"),
    maintenance_statut_id: int | None = Query(None),
):
    from app.crud import affectation as crud_affectation
    from app.crud import statut as crud_statut

    total = await crud_equipement.count_total(db)
    maintenance = 0
    if maintenance_statut_id is not None:
        maintenance = await crud_equipement.count_by_statut(db, maintenance_statut_id)
    else:
        statut = await crud_statut.get_by_nom(db, "En maintenance")
        if statut is not None:
            maintenance = await crud_equipement.count_by_statut(db, statut.id)

    # Indicateurs du module de stock / affectations.
    async def _count(nom: str) -> int:
        s = await crud_statut.get_by_nom(db, nom)
        return await crud_equipement.count_by_statut(db, s.id) if s else 0

    disponibles = await _count("En stock")
    affectes = await _count("Affecte") + await _count("Affecté")
    endommages = await _count("Endommage") + await _count("Endommagé")
    perdus = await _count("Perdu")
    hors_service = await _count("Hors service")

    affectations_actives = await crud_affectation.count_active(db)
    retours_total = await crud_affectation.count_retours(db)

    from sqlalchemy import select
    from app.models.affectation import Affectation
    from app.schemas.equipement import AffectationResume
    from sqlalchemy.orm import selectinload

    recentes_rows = (
        await db.execute(
            select(Affectation)
            .options(selectinload(Affectation.employe), selectinload(Affectation.items))
            .order_by(Affectation.created_at.desc())
            .limit(5)
        )
    ).scalars().unique().all()
    affectations_recentes = [
        AffectationResume(
            id=a.id,
            employe_nom=a.employe.nom_complet if a.employe else "?",
            nombre_items=len(a.items),
            statut=a.statut.value,
            date_affectation=a.date_affectation,
        )
        for a in recentes_rows
    ]

    recent = await crud_equipement.list_recent(db, limit=8)
    return EquipementStats(
        total=total,
        maintenance=maintenance,
        recent=recent,
        disponibles=disponibles,
        affectes=affectes,
        endommages=endommages,
        perdus=perdus,
        hors_service=hors_service,
        affectations_actives=affectations_actives,
        retours_total=retours_total,
        affectations_recentes=affectations_recentes,
    )


@router.post(
    "", response_model=EquipementRead, status_code=status.HTTP_201_CREATED
)
async def create_equipement(
    payload: EquipementCreate,
    request: Request,
    db: DbSession,
    current_user: GestionDep,
):
    return await equipement_service.create_equipement(
        db,
        payload,
        user_id=current_user.id,
        ip=await get_client_ip(request),
    )


@router.get("/{equipement_id}", response_model=EquipementRead)
async def read_equipement(
    equipement_id: int, db: DbSession, current_user: PermDep("stock:read")
):
    return await equipement_service.get_equipement_or_404(db, equipement_id)


@router.get("/{equipement_id}/historique", response_model=list[HistoriqueRead])
async def read_equipement_historique(
    equipement_id: int, db: DbSession, current_user: PermDep("historique:read")
):
    return await crud_historique.list_for_equipement(db, equipement_id)


@router.put("/{equipement_id}", response_model=EquipementRead)
async def update_equipement(
    equipement_id: int,
    payload: EquipementUpdate,
    request: Request,
    db: DbSession,
    current_user: GestionDep,
):
    return await equipement_service.update_equipement(
        db,
        equipement_id,
        payload,
        user_id=current_user.id,
        ip=await get_client_ip(request),
    )


@router.delete("/{equipement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipement(
    equipement_id: int,
    request: Request,
    db: DbSession,
    current_user: GestionDep,
):
    await equipement_service.delete_equipement(
        db,
        equipement_id,
        user_id=current_user.id,
        ip=await get_client_ip(request),
    )
    return None