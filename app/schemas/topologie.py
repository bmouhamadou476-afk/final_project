from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TopologieBase(BaseModel):

    nom: str


class TopologieCreate(TopologieBase):

    pass


class TopologieUpdate(BaseModel):

    nom: str | None = None
    statut: str | None = None


class TopologieResponse(TopologieBase):

    id: int
    gns3_project_id: str | None = None
    statut: str
    date_creation: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )