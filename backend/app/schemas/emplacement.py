from pydantic import BaseModel, Field


class EmplacementBase(BaseModel):
    nom: str = Field(max_length=100)
    batiment: str | None = Field(default=None, max_length=100)
    etage: str | None = Field(default=None, max_length=50)
    salle: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=10000)
    actif: bool = True


class EmplacementCreate(EmplacementBase):
    pass


class EmplacementRead(EmplacementBase):
    model_config = {"from_attributes": True}

    id: int
