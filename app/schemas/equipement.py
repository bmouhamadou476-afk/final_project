from pydantic import BaseModel, ConfigDict


class EquipementBase(BaseModel):

    nom: str
    type_equipement: str = "routeur"

    template_gns3: str
    compute_id: str = "local"

    adresse_ip: str | None = None
    management_ip: str | None = None

    username: str | None = None
    password: str | None = None
    enable_secret: str | None = None

    x: int | None = None
    y: int | None = None


class EquipementCreate(EquipementBase):

    topologie_id: int


class EquipementUpdate(BaseModel):

    nom: str | None = None
    type_equipement: str | None = None

    template_gns3: str | None = None
    compute_id: str | None = None

    adresse_ip: str | None = None
    management_ip: str | None = None

    username: str | None = None
    password: str | None = None
    enable_secret: str | None = None

    x: int | None = None
    y: int | None = None

    actif: bool | None = None


class EquipementResponse(EquipementBase):

    id: int
    actif: bool
    gns3_node_id: str | None = None
    topologie_id: int

    model_config = ConfigDict(
        from_attributes=True
    )