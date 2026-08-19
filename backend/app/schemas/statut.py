from pydantic import BaseModel, Field


class StatutBase(BaseModel):
    nom: str = Field(max_length=50)
    description: str | None = Field(default=None, max_length=10000)
    actif: bool = True


class StatutCreate(StatutBase):
    pass


class StatutRead(StatutBase):
    model_config = {"from_attributes": True}

    id: int
