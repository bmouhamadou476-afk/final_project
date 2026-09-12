from pydantic import BaseModel, ConfigDict


class InterfaceBase(BaseModel):

    nom: str

    adresse_ip: str | None = None
    masque: str | None = None
    description: str | None = None

    adapter: int
    port: int


class InterfaceCreate(InterfaceBase):

    equipement_id: int


class InterfaceUpdate(BaseModel):

    nom: str | None = None

    adresse_ip: str | None = None
    masque: str | None = None
    description: str | None = None

    adapter: int | None = None
    port: int | None = None


class InterfaceResponse(InterfaceBase):

    id: int
    equipement_id: int

    model_config = ConfigDict(
        from_attributes=True
    )