from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.databases import get_db

from app.models.interfaces import Interface
from app.models.equipements import Equipement

from app.schemas.interface import (
    InterfaceCreate,
    InterfaceUpdate,
    InterfaceResponse,
)


router = APIRouter(
    prefix="/api/interfaces",
    tags=["Interfaces"],
)


# ============================================================
# GET - Toutes les interfaces
# ============================================================

@router.get(
    "",
    response_model=list[InterfaceResponse]
)
def get_interfaces(
    db: Session = Depends(get_db)
):

    return db.query(Interface).all()


# ============================================================
# GET - Interface par ID
# ============================================================

@router.get(
    "/{interface_id}",
    response_model=InterfaceResponse
)
def get_interface(
    interface_id: int,
    db: Session = Depends(get_db)
):

    interface = (
        db.query(Interface)
        .filter(Interface.id == interface_id)
        .first()
    )

    if not interface:
        raise HTTPException(
            status_code=404,
            detail="Interface introuvable"
        )

    return interface


# ============================================================
# POST - Créer une interface
# ============================================================

@router.post(
    "",
    response_model=InterfaceResponse,
    status_code=201
)
def create_interface(
    data: InterfaceCreate,
    db: Session = Depends(get_db)
):

    equipement = (
        db.query(Equipement)
        .filter(
            Equipement.id == data.equipement_id
        )
        .first()
    )

    if not equipement:
        raise HTTPException(
            status_code=404,
            detail="Équipement introuvable"
        )

    interface = Interface(
        nom=data.nom,
        adresse_ip=data.adresse_ip,
        masque=data.masque,
        description=data.description,
        adapter=data.adapter,
        port=data.port,
        equipement_id=data.equipement_id
    )

    db.add(interface)
    db.commit()
    db.refresh(interface)

    return interface


# ============================================================
# PUT - Modifier une interface
# ============================================================

@router.put(
    "/{interface_id}",
    response_model=InterfaceResponse
)
def update_interface(
    interface_id: int,
    data: InterfaceUpdate,
    db: Session = Depends(get_db)
):

    interface = (
        db.query(Interface)
        .filter(Interface.id == interface_id)
        .first()
    )

    if not interface:
        raise HTTPException(
            status_code=404,
            detail="Interface introuvable"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            interface,
            key,
            value
        )

    db.commit()
    db.refresh(interface)

    return interface


# ============================================================
# DELETE - Supprimer une interface
# ============================================================

@router.delete(
    "/{interface_id}"
)
def delete_interface(
    interface_id: int,
    db: Session = Depends(get_db)
):

    interface = (
        db.query(Interface)
        .filter(Interface.id == interface_id)
        .first()
    )

    if not interface:
        raise HTTPException(
            status_code=404,
            detail="Interface introuvable"
        )

    db.delete(interface)
    db.commit()

    return {
        "message": "Interface supprimée avec succès",
        "id": interface_id
    }