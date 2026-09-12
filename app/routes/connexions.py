# =============================================================================
# ROUTES CONNEXIONS
# =============================================================================

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.databases import get_db

from app.models.connexions import Connexion
from app.models.topology import Topologie
from app.models.equipements import Equipement
from app.models.interfaces import Interface

from app.schemas.connexion import (
    ConnexionCreate,
    ConnexionUpdate,
    ConnexionResponse,
)


# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter(
    prefix="/api/connexions",
    tags=["Connexions"],
)


# =============================================================================
# GET - LISTE
# =============================================================================

@router.get(
    "",
    response_model=list[ConnexionResponse],
    summary="Lister les connexions",
    description="""
    Retourne toutes les connexions réseau enregistrées.

    Une connexion relie deux interfaces appartenant à deux équipements.
    """,
    response_description="Liste des connexions",
)
def get_connexions(
    db: Session = Depends(get_db),
):

    return db.query(
        Connexion
    ).all()


# =============================================================================
# POST - CRÉATION
# =============================================================================

@router.post(
    "",
    response_model=ConnexionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une connexion",
    description="""
    Crée une connexion entre deux interfaces réseau.

    La connexion est enregistrée dans MySQL puis pourra être
    automatiquement créée dans GNS3 lors du déploiement.

    Les ports et adaptateurs GNS3 sont récupérés depuis les
    interfaces concernées.
    """,
    response_description="Connexion créée",
)
def create_connexion(
    data: ConnexionCreate,
    db: Session = Depends(get_db),
):

    # -------------------------------------------------------------------------
    # Vérification topologie
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Vérification équipement source
    # -------------------------------------------------------------------------

    source = (
        db.query(Equipement)
        .filter(
            Equipement.id
            == data.equipement_source_id
        )
        .first()
    )

    if not source:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipement source introuvable.",
        )

    # -------------------------------------------------------------------------
    # Vérification équipement destination
    # -------------------------------------------------------------------------

    destination = (
        db.query(Equipement)
        .filter(
            Equipement.id
            == data.equipement_destination_id
        )
        .first()
    )

    if not destination:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipement destination introuvable.",
        )

    # -------------------------------------------------------------------------
    # Vérification interface source
    # -------------------------------------------------------------------------

    interface_source = (
        db.query(Interface)
        .filter(
            Interface.id
            == data.interface_source_id
        )
        .first()
    )

    if not interface_source:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interface source introuvable.",
        )

    # -------------------------------------------------------------------------
    # Vérification interface destination
    # -------------------------------------------------------------------------

    interface_destination = (
        db.query(Interface)
        .filter(
            Interface.id
            == data.interface_destination_id
        )
        .first()
    )

    if not interface_destination:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interface destination introuvable.",
        )

    # -------------------------------------------------------------------------
    # Vérification propriétaire interface source
    # -------------------------------------------------------------------------

    if (
        interface_source.equipement_id
        != source.id
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "L'interface source "
                "n'appartient pas à "
                "l'équipement source."
            ),
        )

    # -------------------------------------------------------------------------
    # Vérification propriétaire interface destination
    # -------------------------------------------------------------------------

    if (
        interface_destination.equipement_id
        != destination.id
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "L'interface destination "
                "n'appartient pas à "
                "l'équipement destination."
            ),
        )

    # -------------------------------------------------------------------------
    # Vérification topologie des équipements
    # -------------------------------------------------------------------------

    if source.topologie_id != data.topologie_id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "L'équipement source "
                "n'appartient pas à cette topologie."
            ),
        )

    if destination.topologie_id != data.topologie_id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "L'équipement destination "
                "n'appartient pas à cette topologie."
            ),
        )

    # -------------------------------------------------------------------------
    # Création
    # -------------------------------------------------------------------------

    connexion = Connexion(
        equipement_source_id=data.equipement_source_id,
        interface_source_id=data.interface_source_id,

        equipement_destination_id=data.equipement_destination_id,
        interface_destination_id=data.interface_destination_id,

        topologie_id=data.topologie_id,
    )

    db.add(connexion)

    db.commit()

    db.refresh(connexion)

    return connexion


# =============================================================================
# GET - UNE CONNEXION
# =============================================================================

@router.get(
    "/{connexion_id}",
    response_model=ConnexionResponse,
    summary="Récupérer une connexion",
    description="""
    Retourne une connexion réseau à partir de son identifiant.
    """,
    response_description="Connexion demandée",
)
def get_connexion(
    connexion_id: int,
    db: Session = Depends(get_db),
):

    connexion = (
        db.query(Connexion)
        .filter(
            Connexion.id == connexion_id
        )
        .first()
    )

    if not connexion:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connexion introuvable.",
        )

    return connexion


# =============================================================================
# PUT - MODIFICATION
# =============================================================================

@router.put(
    "/{connexion_id}",
    response_model=ConnexionResponse,
    summary="Modifier une connexion",
    description="""
    Modifie les équipements ou interfaces associés à une connexion.
    """,
    response_description="Connexion modifiée",
)
def update_connexion(
    connexion_id: int,
    data: ConnexionUpdate,
    db: Session = Depends(get_db),
):

    connexion = (
        db.query(Connexion)
        .filter(
            Connexion.id == connexion_id
        )
        .first()
    )

    if not connexion:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connexion introuvable.",
        )

    values = data.model_dump(
        exclude_unset=True
    )

    for field, value in values.items():

        setattr(
            connexion,
            field,
            value,
        )

    db.commit()

    db.refresh(connexion)

    return connexion


# =============================================================================
# DELETE - SUPPRESSION
# =============================================================================

@router.delete(
    "/{connexion_id}",
    summary="Supprimer une connexion",
    description="""
    Supprime une connexion de la base de données.

    Lors d'un nouveau déploiement, la topologie GNS3 sera reconstruite
    à partir des connexions actuellement présentes dans MySQL.
    """,
    response_description="Confirmation de suppression",
)
def delete_connexion(
    connexion_id: int,
    db: Session = Depends(get_db),
):

    connexion = (
        db.query(Connexion)
        .filter(
            Connexion.id == connexion_id
        )
        .first()
    )

    if not connexion:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connexion introuvable.",
        )

    db.delete(connexion)

    db.commit()

    return {
        "message": "Connexion supprimée avec succès.",
        "connexion_id": connexion_id,
    }