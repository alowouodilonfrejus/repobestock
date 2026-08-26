from fastapi import APIRouter

from app.api.routes import (
    affectations,
    auth,
    categories,
    emplacements,
    employes,
    equipements,
    fournisseurs,
    historique,
    maintenances,
    mouvements,
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
api_router.include_router(employes.router)
api_router.include_router(fournisseurs.router)
api_router.include_router(affectations.router)
api_router.include_router(maintenances.router)
api_router.include_router(mouvements.router)
