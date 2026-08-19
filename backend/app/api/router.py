from fastapi import APIRouter

from app.api.routes import (
    auth,
    categories,
    emplacements,
    equipements,
    historique,
    statuts,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(categories.router)
api_router.include_router(statuts.router)
api_router.include_router(emplacements.router)
api_router.include_router(equipements.router)
api_router.include_router(historique.router)
api_router.include_router(users.router)
