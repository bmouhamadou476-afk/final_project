from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.databases import get_db

from app.models.connexions import Connexion
from app.models.equipements import Equipement
from app.models.interfaces import Interface

from app.schemas.connexion import (
    ConnexionCreate,
    ConnexionUpdate,
    ConnexionResponse,
)


router = APIRouter(
    prefix="/api/connexions",
    tags=["Connexions"],
)


# ============================================================
# GET - Toutes les connexions
# ============================================================

@router.get(
    "",
    response_model=list[ConnexionResponse]
)
def get_connexions(
    db: Session = Depends(get_db)
):

    return db.query(Connexion).all()


# ============================================================
# GET - Connexion par ID
# ============================================================

@router.get(
    "/{connexion_id}",
    response_model=ConnexionResponse
)
def get_connexion(
    connexion_id: int,
    db: Session = Depends(get_db)
):

    connexion = (
        db.query(Connexion)
        .filter(Connexion.id == connexion_id)
        .first()
    )

    if not connexion:
        raise HTTPException(
            status_code=404,
            detail="Connexion introuvable"
        )

    return connexion


# ============================================================
# POST - Créer une connexion
# ============================================================

@router.post(
    "",
    response_model=ConnexionResponse,
    status_code=201
)
def create_connexion(
    data: ConnexionCreate,
    db: Session = Depends(get_db)
):

    source = (
        db.query(Equipement)
        .filter(
            Equipement.id == data.equipement_source_id
        )
        .first()
    )

    destination = (
        db.query(Equipement)
        .filter(
            Equipement.id == data.equipement_destination_id
        )
        .first()
    )

    if not source:
        raise HTTPException(
            status_code=404,
            detail="Équipement source introuvable"
        )

    if not destination:
        raise HTTPException(
            status_code=404,
            detail="Équipement destination introuvable"
        )

    interface_source = (
        db.query(Interface)
        .filter(
            Interface.id == data.interface_source_id
        )
        .first()
    )

    interface_destination = (
        db.query(Interface)
        .filter(
            Interface.id == data.interface_destination_id
        )
        .first()
    )

    if not interface_source:
        raise HTTPException(
            status_code=404,
            detail="Interface source introuvable"
        )

    if not interface_destination:
        raise HTTPException(
            status_code=404,
            detail="Interface destination introuvable"
        )

    # Vérifier que les interfaces appartiennent
    # bien aux équipements indiqués

    if interface_source.equipement_id != source.id:
        raise HTTPException(
            status_code=400,
            detail="L'interface source n'appartient pas à l'équipement source"
        )

    if interface_destination.equipement_id != destination.id:
        raise HTTPException(
            status_code=400,
            detail="L'interface destination n'appartient pas à l'équipement destination"
        )

    connexion = Connexion(
        equipement_source_id=data.equipement_source_id,
        interface_source_id=data.interface_source_id,
        equipement_destination_id=data.equipement_destination_id,
        interface_destination_id=data.interface_destination_id,
        topologie_id=data.topologie_id
    )

    db.add(connexion)
    db.commit()
    db.refresh(connexion)

    return connexion


# ============================================================
# PUT - Modifier une connexion
# ============================================================

@router.put(
    "/{connexion_id}",
    response_model=ConnexionResponse
)
def update_connexion(
    connexion_id: int,
    data: ConnexionUpdate,
    db: Session = Depends(get_db)
):

    connexion = (
        db.query(Connexion)
        .filter(Connexion.id == connexion_id)
        .first()
    )

    if not connexion:
        raise HTTPException(
            status_code=404,
            detail="Connexion introuvable"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            connexion,
            key,
            value
        )

    db.commit()
    db.refresh(connexion)

    return connexion


# ============================================================
# DELETE - Supprimer une connexion
# ============================================================

@router.delete(
    "/{connexion_id}"
)
def delete_connexion(
    connexion_id: int,
    db: Session = Depends(get_db)
):

    connexion = (
        db.query(Connexion)
        .filter(Connexion.id == connexion_id)
        .first()
    )

    if not connexion:
        raise HTTPException(
            status_code=404,
            detail="Connexion introuvable"
        )

    db.delete(connexion)
    db.commit()

    return {
        "message": "Connexion supprimée avec succès",
        "id": connexion_id
    }