from fastapi import APIRouter, status

from app.api.deps import ActiveUser, DbSession, PermDep
from app.crud import fournisseur as crud_fournisseur
from app.models.user import UserRole
from app.schemas.fournisseur import (
    FournisseurCreate,
    FournisseurList,
    FournisseurRead,
)

router = APIRouter(prefix="/fournisseurs", tags=["fournisseurs"])

WriteDep = PermDep("fournisseurs:write")


@router.get("", response_model=FournisseurList)
async def read_fournisseurs(db: DbSession, current_user: PermDep("fournisseurs:read")):
    items, total = await crud_fournisseur.list_fournisseurs(db)
    return FournisseurList(items=items, total=total)


@router.post(
    "", response_model=FournisseurRead, status_code=status.HTTP_201_CREATED
)
async def create_fournisseur(
    payload: FournisseurCreate, db: DbSession, _: WriteDep
):
    """Cree un fournisseur ; renvoie l'existant si le nom est deja pris."""
    existant = await crud_fournisseur.get_by_nom(db, payload.nom)
    if existant is not None:
        return existant
    return await crud_fournisseur.create(db, payload.nom, payload.contact)
