# =============================================================================
# ROUTES ÉQUIPEMENTS
# =============================================================================

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.databases import get_db

from app.models.equipements import Equipement
from app.models.topology import Topologie

from app.schemas.equipement import (
    EquipementCreate,
    EquipementUpdate,
    EquipementResponse,
)


# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter(
    prefix="/api/equipements",
    tags=["Équipements"],
)


# =============================================================================
# GET - LISTE
# =============================================================================

@router.get(
    "",
    response_model=list[EquipementResponse],
    summary="Lister les équipements",
    description="""
    Retourne tous les équipements enregistrés.

    Les équipements peuvent être associés à une topologie
    et à un projet GNS3.
    """,
    response_description="Liste des équipements",
)
def get_equipements(
    db: Session = Depends(get_db),
):

    return db.query(
        Equipement
    ).all()


# =============================================================================
# POST - CRÉATION
# =============================================================================

@router.post(
    "",
    response_model=EquipementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un équipement",
    description="""
    Crée un équipement réseau dans une topologie.

    Les informations GNS3 peuvent être renseignées dès la création :

    - template GNS3 ;
    - compute ;
    - position X/Y.

    Les paramètres de management permettent ensuite
    l'automatisation SSH avec Netmiko.
    """,
    response_description="Équipement créé",
)
def create_equipement(
    data: EquipementCreate,
    db: Session = Depends(get_db),
):

    topologie = (
        db.query(Topologie)
        .filter(
            Topologie.id == data.topologie_id
        )
        .first()
    )

    if not topologie:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topologie introuvable.",
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
        actif=False,
    )

    db.add(equipement)

    db.commit()

    db.refresh(equipement)

    return equipement


# =============================================================================
# GET - UN ÉQUIPEMENT
# =============================================================================

@router.get(
    "/{equipement_id}",
    response_model=EquipementResponse,
    summary="Récupérer un équipement",
    description="""
    Retourne les informations d'un équipement à partir de son identifiant.
    """,
    response_description="Équipement demandé",
)
def get_equipement(
    equipement_id: int,
    db: Session = Depends(get_db),
):

    equipement = (
        db.query(Equipement)
        .filter(
            Equipement.id == equipement_id
        )
        .first()
    )

    if not equipement:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipement introuvable.",
        )

    return equipement


# =============================================================================
# PUT - MODIFICATION
# =============================================================================

@router.put(
    "/{equipement_id}",
    response_model=EquipementResponse,
    summary="Modifier un équipement",
    description="""
    Modifie la configuration d'un équipement existant.

    Les paramètres de management et les informations GNS3
    peuvent également être modifiés.
    """,
    response_description="Équipement modifié",
)
def update_equipement(
    equipement_id: int,
    data: EquipementUpdate,
    db: Session = Depends(get_db),
):

    equipement = (
        db.query(Equipement)
        .filter(
            Equipement.id == equipement_id
        )
        .first()
    )

    if not equipement:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipement introuvable.",
        )

    values = data.model_dump(
        exclude_unset=True
    )

    for field, value in values.items():

        setattr(
            equipement,
            field,
            value,
        )

    db.commit()

    db.refresh(equipement)

    return equipement


# =============================================================================
# DELETE - SUPPRESSION
# =============================================================================

@router.delete(
    "/{equipement_id}",
    summary="Supprimer un équipement",
    description="""
    Supprime un équipement de la base de données.

    Les interfaces associées sont également supprimées
    selon la relation définie dans le modèle SQLAlchemy.
    """,
    response_description="Confirmation de suppression",
)
def delete_equipement(
    equipement_id: int,
    db: Session = Depends(get_db),
):

    equipement = (
        db.query(Equipement)
        .filter(
            Equipement.id == equipement_id
        )
        .first()
    )

    if not equipement:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipement introuvable.",
        )

    db.delete(equipement)

    db.commit()

    return {
        "message": "Équipement supprimé avec succès.",
        "equipement_id": equipement_id,
    }