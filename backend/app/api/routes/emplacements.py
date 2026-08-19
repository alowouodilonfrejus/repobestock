from fastapi import APIRouter

from app.api.deps import ActiveUser, DbSession
from app.crud import emplacement as crud_emplacement
from app.schemas.emplacement import EmplacementRead

router = APIRouter(prefix="/emplacements", tags=["emplacements"])


@router.get("", response_model=list[EmplacementRead])
async def read_emplacements(db: DbSession, current_user: ActiveUser):
    return await crud_emplacement.list_emplacements(db)
