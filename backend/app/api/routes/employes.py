from fastapi import APIRouter, Query, status

from app.api.deps import ActiveUser, DbSession, PermDep
from app.crud import employe as crud_employe
from app.models.user import UserRole
from app.schemas.employe import (
    EmployeCreate,
    EmployeInscriptionCreate,
    EmployeRead,
    EmployeUpdate,
    EmployeWithAccountCreate,
)
from app.schemas.employe import MaterielAttribue
from app.services import affectation as affectation_service
from app.services import employe as employe_service

router = APIRouter(prefix="/employes", tags=["employes"])

GestionDep = PermDep("employes:write")


@router.get("", response_model=list[EmployeRead])
async def read_employes(
    db: DbSession,
    current_user: PermDep("employes:read"),
    actif: bool | None = Query(None),
):
    items, _total = await crud_employe.list_employes(db, actif=actif)
    return items


@router.get("/moi", response_model=list[MaterielAttribue])
async def read_mes_materiels(db: DbSession, current_user: ActiveUser):
    """Materiels attribues au compte connecte (si rattache a un employe)."""
    employe = await crud_employe.get_by_user_id(db, current_user.id)
    if employe is None:
        return []
    items = await affectation_service.list_materiels_attribues(db, employe.id)
    return [
        MaterielAttribue(
            affectation_item_id=item.id,
            equipement_id=item.equipement_id,
            reference=item.equipement_reference,
            nom=item.equipement_nom,
            quantite=item.quantite,
            etat_affectation=item.etat_affectation,
            date_affectation=item.affectation.date_affectation,
            date_retour_prevue=item.affectation.date_retour_prevue,
        )
        for item in items
    ]


@router.post(
    "", response_model=EmployeRead, status_code=status.HTTP_201_CREATED
)
async def create_employe(payload: EmployeCreate, db: DbSession, _: GestionDep):
    return await employe_service.create_employe(db, payload)


@router.post(
    "/avec-compte", response_model=EmployeRead, status_code=status.HTTP_201_CREATED
)
async def create_employe_avec_compte(
    payload: EmployeWithAccountCreate, db: DbSession, current_user: GestionDep
):
    """Crée un employé ET son compte de connexion en une requête.

    Le compte est actif immédiatement (pas d'attente de validation) avec le rôle
    `manager` par défaut — l'employé peut se connecter sur `/connexion` et
    accéder à `Mon matériel`.
    """
    return await employe_service.create_employe_with_account(db, payload, current_user)


@router.post(
    "/inscription", status_code=status.HTTP_201_CREATED
)
async def inscrire_employe(payload: EmployeInscriptionCreate, db: DbSession):
    """Inscription publique d'un employé.

    Crée la fiche employé ET un compte de connexion inactif : l'employé
    attend la validation d'un admin ou du super admin avant de pouvoir
    se connecter.
    """
    return await employe_service.register_employe(db, payload)


@router.get("/{employe_id}", response_model=EmployeRead)
async def read_employe(employe_id: int, db: DbSession, current_user: PermDep("employes:read")):
    return await employe_service.get_employe_or_404(db, employe_id)


@router.get("/{employe_id}/materiels", response_model=list[MaterielAttribue])
async def read_materiels_employe(
    employe_id: int, db: DbSession, current_user: PermDep("employes:read")
):
    """Section 'Materiels attribues' de la fiche employe."""
    await employe_service.get_employe_or_404(db, employe_id)
    items = await affectation_service.list_materiels_attribues(db, employe_id)
    return [
        MaterielAttribue(
            affectation_item_id=item.id,
            equipement_id=item.equipement_id,
            reference=item.equipement_reference,
            nom=item.equipement_nom,
            quantite=item.quantite,
            etat_affectation=item.etat_affectation,
            date_affectation=item.affectation.date_affectation,
            date_retour_prevue=item.affectation.date_retour_prevue,
        )
        for item in items
    ]


@router.put("/{employe_id}", response_model=EmployeRead)
async def update_employe(
    employe_id: int, payload: EmployeUpdate, db: DbSession, _: GestionDep
):
    return await employe_service.update_employe(db, employe_id, payload)
