from pydantic import BaseModel, ConfigDict


class ConnexionCreate(BaseModel):

    equipement_source_id: int
    interface_source_id: int

    equipement_destination_id: int
    interface_destination_id: int

    topologie_id: int


class ConnexionUpdate(BaseModel):

    equipement_source_id: int | None = None
    interface_source_id: int | None = None

    equipement_destination_id: int | None = None
    interface_destination_id: int | None = None


class ConnexionResponse(BaseModel):

    id: int

    gns3_link_id: str | None = None

    equipement_source_id: int
    interface_source_id: int

    equipement_destination_id: int
    interface_destination_id: int

    topologie_id: int

    model_config = ConfigDict(
        from_attributes=True
    )