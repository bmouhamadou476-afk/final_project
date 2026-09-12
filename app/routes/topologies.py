from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.databases import get_db

from app.models.topology import Topologie

from app.schemas.topologie import (
    TopologieCreate,
    TopologieUpdate,
    TopologieResponse,
)


router = APIRouter(
    prefix="/api/topologies",
    tags=["Topologies"],
)


# ============================================================
# GET - Lister toutes les topologies
# ============================================================

@router.get(
    "",
    response_model=list[TopologieResponse]
)
def get_topologies(
    db: Session = Depends(get_db)
):

    return db.query(Topologie).all()


# ============================================================
# GET - Récupérer une topologie par son ID
# ============================================================

@router.get(
    "/{topologie_id}",
    response_model=TopologieResponse
)
def get_topologie(
    topologie_id: int,
    db: Session = Depends(get_db)
):

    topologie = (
        db.query(Topologie)
        .filter(Topologie.id == topologie_id)
        .first()
    )

    if not topologie:
        raise HTTPException(
            status_code=404,
            detail="Topologie introuvable"
        )

    return topologie


# ============================================================
# POST - Créer une topologie
# ============================================================

@router.post(
    "",
    response_model=TopologieResponse,
    status_code=201
)
def create_topologie(
    data: TopologieCreate,
    db: Session = Depends(get_db)
):

    # Vérifier si le nom existe déjà
    existing = (
        db.query(Topologie)
        .filter(Topologie.nom == data.nom)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Une topologie avec ce nom existe déjà"
        )

    topologie = Topologie(
        nom=data.nom,
        statut="created"
    )

    db.add(topologie)
    db.commit()
    db.refresh(topologie)

    return topologie


# ============================================================
# PUT - Modifier une topologie
# ============================================================

@router.put(
    "/{topologie_id}",
    response_model=TopologieResponse
)
def update_topologie(
    topologie_id: int,
    data: TopologieUpdate,
    db: Session = Depends(get_db)
):

    topologie = (
        db.query(Topologie)
        .filter(Topologie.id == topologie_id)
        .first()
    )

    if not topologie:
        raise HTTPException(
            status_code=404,
            detail="Topologie introuvable"
        )

    if data.nom is not None:

        existing = (
            db.query(Topologie)
            .filter(
                Topologie.nom == data.nom,
                Topologie.id != topologie_id
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Une topologie avec ce nom existe déjà"
            )

        topologie.nom = data.nom

    if data.statut is not None:
        topologie.statut = data.statut

    db.commit()
    db.refresh(topologie)

    return topologie


# ============================================================
# DELETE - Supprimer une topologie
# ============================================================

@router.delete(
    "/{topologie_id}"
)
def delete_topologie(
    topologie_id: int,
    db: Session = Depends(get_db)
):

    topologie = (
        db.query(Topologie)
        .filter(Topologie.id == topologie_id)
        .first()
    )

    if not topologie:
        raise HTTPException(
            status_code=404,
            detail="Topologie introuvable"
        )

    db.delete(topologie)
    db.commit()

    return {
        "message": "Topologie supprimée avec succès",
        "id": topologie_id
    }