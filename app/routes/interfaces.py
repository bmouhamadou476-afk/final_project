# =============================================================================
# ROUTES INTERFACES
# =============================================================================

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.databases import get_db

from app.models.interfaces import Interface
from app.models.equipements import Equipement

from app.schemas.interface import (
    InterfaceCreate,
    InterfaceUpdate,
    InterfaceResponse,
)


# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter(
    prefix="/api/interfaces",
    tags=["Interfaces"],
)


# =============================================================================
# GET - LISTE
# =============================================================================

@router.get(
    "",
    response_model=list[InterfaceResponse],
    summary="Lister les interfaces",
    description="""
    Retourne toutes les interfaces enregistrées dans la base de données.

    Chaque interface contient notamment :

    - son nom ;
    - son adresse IP ;
    - son masque ;
    - sa description ;
    - son numéro d'adaptateur GNS3 ;
    - son numéro de port GNS3 ;
    - son équipement parent.
    """,
    response_description="Liste des interfaces",
)
def get_interfaces(
    db: Session = Depends(get_db),
):

    return db.query(
        Interface
    ).all()


# =============================================================================
# POST - CRÉATION
# =============================================================================

@router.post(
    "",
    response_model=InterfaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une interface",
    description="""
    Crée une interface réseau et l'associe à un équipement.

    L'adresse IP et le masque seront utilisés automatiquement
    lors du déploiement pour configurer l'interface sur le routeur.

    Les valeurs `adapter` et `port` correspondent aux interfaces
    utilisées par GNS3 pour créer les connexions.
    """,
    response_description="Interface créée",
)
def create_interface(
    data: InterfaceCreate,
    db: Session = Depends(get_db),
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipement introuvable.",
        )

    interface = Interface(
        nom=data.nom,
        adresse_ip=data.adresse_ip,
        masque=data.masque,
        description=data.description,
        adapter=data.adapter,
        port=data.port,
        equipement_id=data.equipement_id,
    )

    db.add(interface)

    db.commit()

    db.refresh(interface)

    return interface


# =============================================================================
# GET - UNE INTERFACE
# =============================================================================

@router.get(
    "/{interface_id}",
    response_model=InterfaceResponse,
    summary="Récupérer une interface",
    description="""
    Retourne les informations d'une interface à partir de son identifiant.
    """,
    response_description="Interface demandée",
)
def get_interface(
    interface_id: int,
    db: Session = Depends(get_db),
):

    interface = (
        db.query(Interface)
        .filter(
            Interface.id == interface_id
        )
        .first()
    )

    if not interface:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interface introuvable.",
        )

    return interface


# =============================================================================
# PUT - MODIFICATION
# =============================================================================

@router.put(
    "/{interface_id}",
    response_model=InterfaceResponse,
    summary="Modifier une interface",
    description="""
    Modifie la configuration d'une interface existante.

    Les modifications seront prises en compte lors du prochain
    déploiement de la topologie.
    """,
    response_description="Interface modifiée",
)
def update_interface(
    interface_id: int,
    data: InterfaceUpdate,
    db: Session = Depends(get_db),
):

    interface = (
        db.query(Interface)
        .filter(
            Interface.id == interface_id
        )
        .first()
    )

    if not interface:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interface introuvable.",
        )

    values = data.model_dump(
        exclude_unset=True
    )

    for field, value in values.items():

        setattr(
            interface,
            field,
            value,
        )

    db.commit()

    db.refresh(interface)

    return interface


# =============================================================================
# DELETE - SUPPRESSION
# =============================================================================

@router.delete(
    "/{interface_id}",
    summary="Supprimer une interface",
    description="""
    Supprime une interface de la base de données.
    """,
    response_description="Confirmation de suppression",
)
def delete_interface(
    interface_id: int,
    db: Session = Depends(get_db),
):

    interface = (
        db.query(Interface)
        .filter(
            Interface.id == interface_id
        )
        .first()
    )

    if not interface:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interface introuvable.",
        )

    db.delete(interface)

    db.commit()

    return {
        "message": "Interface supprimée avec succès.",
        "interface_id": interface_id,
    }