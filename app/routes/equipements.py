from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.databases import get_db

from app.models.equipements import Equipement
from app.models.topology import Topologie

from app.schemas.equipement import (
    EquipementCreate,
    EquipementUpdate,
    EquipementResponse,
)


router = APIRouter(
    prefix="/api/equipements",
    tags=["Équipements"],
)


# ============================================================
# GET - Tous les équipements
# ============================================================

@router.get(
    "",
    response_model=list[EquipementResponse]
)
def get_equipements(
    db: Session = Depends(get_db)
):

    return db.query(Equipement).all()


# ============================================================
# GET - Équipement par ID
# ============================================================

@router.get(
    "/{equipement_id}",
    response_model=EquipementResponse
)
def get_equipement(
    equipement_id: int,
    db: Session = Depends(get_db)
):

    equipement = (
        db.query(Equipement)
        .filter(Equipement.id == equipement_id)
        .first()
    )

    if not equipement:
        raise HTTPException(
            status_code=404,
            detail="Équipement introuvable"
        )

    return equipement


# ============================================================
# POST - Créer un équipement
# ============================================================

@router.post(
    "",
    response_model=EquipementResponse,
    status_code=201
)
def create_equipement(
    data: EquipementCreate,
    db: Session = Depends(get_db)
):

    # Vérifier que la topologie existe
    topologie = (
        db.query(Topologie)
        .filter(Topologie.id == data.topologie_id)
        .first()
    )

    if not topologie:
        raise HTTPException(
            status_code=404,
            detail="Topologie introuvable"
        )

    equipement = Equipement(
        nom=data.nom,
        type_equipement=data.type_equipement,
        template_gns3=data.template_gns3,
        compute_id=data.compute_id,
        adresse_ip=data.adresse_ip,
        management_ip=data.management_ip,
        username=data.username,
        password=data.password,
        enable_secret=data.enable_secret,
        x=data.x,
        y=data.y,
        topologie_id=data.topologie_id,
        actif=False
    )

    db.add(equipement)
    db.commit()
    db.refresh(equipement)

    return equipement


# ============================================================
# PUT - Modifier un équipement
# ============================================================

@router.put(
    "/{equipement_id}",
    response_model=EquipementResponse
)
def update_equipement(
    equipement_id: int,
    data: EquipementUpdate,
    db: Session = Depends(get_db)
):

    equipement = (
        db.query(Equipement)
        .filter(Equipement.id == equipement_id)
        .first()
    )

    if not equipement:
        raise HTTPException(
            status_code=404,
            detail="Équipement introuvable"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            equipement,
            key,
            value
        )

    db.commit()
    db.refresh(equipement)

    return equipement


# ============================================================
# DELETE - Supprimer un équipement
# ============================================================

@router.delete(
    "/{equipement_id}"
)
def delete_equipement(
    equipement_id: int,
    db: Session = Depends(get_db)
):

    equipement = (
        db.query(Equipement)
        .filter(Equipement.id == equipement_id)
        .first()
    )

    if not equipement:
        raise HTTPException(
            status_code=404,
            detail="Équipement introuvable"
        )

    db.delete(equipement)
    db.commit()

    return {
        "message": "Équipement supprimé avec succès",
        "id": equipement_id
    }