"""Logique metier des employes."""

import secrets

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.crud import employe as crud_employe
from app.crud import user as crud_user
from app.models.employe import Employe
from app.models.user import User, UserRole
from app.schemas.employe import (
    EmployeCreate,
    EmployeInscriptionCreate,
    EmployeUpdate,
    EmployeWithAccountCreate,
)


async def get_employe_or_404(db: AsyncSession, employe_id: int) -> Employe:
    employe = await crud_employe.get_by_id(db, employe_id)
    if employe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employe introuvable"
        )
    return employe


async def _verifier_matricule_unique(
    db: AsyncSession, matricule: str, exclude_id: int | None = None
) -> None:
    existant = await crud_employe.get_by_matricule(db, matricule)
    if existant is not None and existant.id != exclude_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce matricule existe deja",
        )


async def _verifier_user_id(db: AsyncSession, user_id: int) -> None:
    if await crud_user.get_by_id(db, user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Utilisateur {user_id} introuvable",
        )


async def create_employe(db: AsyncSession, payload: EmployeCreate) -> Employe:
    await _verifier_matricule_unique(db, payload.matricule)
    if payload.user_id is not None:
        await _verifier_user_id(db, payload.user_id)

    employe = Employe(**payload.model_dump())
    return await crud_employe.create(db, employe)


async def _resoudre_username(
    db: AsyncSession, email: str, username_explicit: str | None
) -> str:
    username = (username_explicit or email.split("@")[0]).strip()
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un nom d'utilisateur valide est requis",
        )
    if username_explicit and await crud_user.get_by_username(db, username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur est déjà utilisé par un autre compte",
        )
    base_username = username
    suffix = 2
    while await crud_user.get_by_username(db, username):
        username = f"{base_username}-{suffix}"
        suffix += 1
    return username


async def _generer_matricule(db: AsyncSession) -> str:
    while True:
        matricule = f"EMP-{secrets.token_hex(3).upper()}"
        if await crud_employe.get_by_matricule(db, matricule) is None:
            return matricule


async def create_employe_with_account(
    db: AsyncSession, payload: EmployeWithAccountCreate, current_user: User
) -> Employe:
    await _verifier_matricule_unique(db, payload.matricule)
    if not payload.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un email est requis pour créer le compte de connexion",
        )
    email = payload.email.lower()
    if await crud_user.get_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est déjà utilisé par un autre compte",
        )
    role = UserRole.MANAGER
    if payload.role:
        role_str = payload.role.lower()
        if role_str not in ("admin", "manager", "employe"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rôle invalide (admin, manager ou employe)",
            )
        role = UserRole(role_str)
        if role == UserRole.ADMIN and current_user.role != UserRole.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seul un super admin peut créer un compte admin",
            )

    username = await _resoudre_username(db, email, payload.username)

    data = payload.model_dump(exclude={"username", "password", "role"})

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(payload.password),
        role=role,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    data["user_id"] = user.id
    employe = Employe(**data)
    db.add(employe)
    await db.commit()
    await db.refresh(user)
    await db.refresh(employe)
    return employe


async def register_employe(
    db: AsyncSession, payload: EmployeInscriptionCreate
) -> dict:
    """Inscription publique : compte inactif + fiche employé liée, en attente de validation."""
    email = payload.email.lower()
    if await crud_user.get_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est déjà utilisé par un autre compte",
        )
    if payload.matricule:
        await _verifier_matricule_unique(db, payload.matricule)
        matricule = payload.matricule
    else:
        matricule = await _generer_matricule(db)

    username = await _resoudre_username(db, email, payload.username)

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(payload.password),
        role=UserRole.EMPLOYE,
        is_active=False,
    )
    db.add(user)
    await db.flush()

    employe = Employe(
        nom_complet=payload.nom_complet.strip(),
        matricule=matricule,
        departement=payload.departement,
        fonction=payload.fonction,
        telephone=payload.telephone,
        date_arrivee=payload.date_arrivee,
        email=email,
        actif=True,
        user_id=user.id,
    )
    db.add(employe)
    await db.commit()
    await db.refresh(user)
    await db.refresh(employe)
    return {
        "message": (
            "Inscription enregistrée. Votre compte sera activé après "
            "validation par un administrateur."
        ),
        "email": email,
        "matricule": matricule,
    }


async def update_employe(
    db: AsyncSession, employe_id: int, payload: EmployeUpdate
) -> Employe:
    employe = await get_employe_or_404(db, employe_id)
    data = payload.model_dump(exclude_unset=True)

    if "matricule" in data and data["matricule"] != employe.matricule:
        await _verifier_matricule_unique(db, data["matricule"], exclude_id=employe_id)

    for key, value in data.items():
        setattr(employe, key, value)
    db.add(employe)
    await db.commit()
    await db.refresh(employe)
    return employe
