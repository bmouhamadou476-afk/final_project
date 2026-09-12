# =============================================================================
# ROUTES TOPOLOGIES
# =============================================================================

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.databases import get_db

from app.models.topology import Topologie

from app.schemas.topologie import (
    TopologieCreate,
    TopologieUpdate,
    TopologieResponse,
)


# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter(
    prefix="/api/topologies",
    tags=["Topologies"],
)


# =============================================================================
# GET - LISTE DES TOPOLOGIES
# =============================================================================

@router.get(
    "",
    response_model=list[TopologieResponse],
    summary="Lister les topologies",
    description="""
    Retourne la liste de toutes les topologies enregistrées
    dans la base de données.

    Chaque topologie contient notamment :

    - son identifiant ;
    - son nom ;
    - son identifiant de projet GNS3 ;
    - son statut ;
    - sa date de création.
    """,
    response_description="Liste des topologies",
)
def get_topologies(
    db: Session = Depends(get_db),
):

    return db.query(
        Topologie
    ).all()


# =============================================================================
# POST - CRÉER UNE TOPOLOGIE
# =============================================================================

@router.post(
    "",
    response_model=TopologieResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une topologie",
    description="""
    Crée une nouvelle topologie réseau dans MySQL.

    Une topologie constitue le conteneur logique des :

    - équipements ;
    - interfaces ;
    - connexions.

    Le projet GNS3 sera associé à la topologie lors du déploiement.
    """,
    response_description="Topologie créée",
)
def create_topologie(
    data: TopologieCreate,
    db: Session = Depends(get_db),
):

    existing = (
        db.query(Topologie)
        .filter(
            Topologie.nom == data.nom
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une topologie portant ce nom existe déjà.",
        )

    topologie = Topologie(
        nom=data.nom,
        statut="created",
    )

    db.add(topologie)

    db.commit()

    db.refresh(topologie)

    return topologie


# =============================================================================
# GET - UNE TOPOLOGIE
# =============================================================================

@router.get(
    "/{topologie_id}",
    response_model=TopologieResponse,
    summary="Récupérer une topologie",
    description="""
    Retourne les informations d'une topologie à partir de son identifiant.
    """,
    response_description="Topologie demandée",
)
def get_topologie(
    topologie_id: int,
    db: Session = Depends(get_db),
):

    topologie = (
        db.query(Topologie)
        .filter(
            Topologie.id == topologie_id
        )
        .first()
    )

    if not topologie:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topologie introuvable.",
        )

    return topologie


# =============================================================================
# PUT - MODIFIER UNE TOPOLOGIE
# =============================================================================

@router.put(
    "/{topologie_id}",
    response_model=TopologieResponse,
    summary="Modifier une topologie",
    description="""
    Modifie les informations d'une topologie existante.

    Les champs fournis sont appliqués à la topologie.
    """,
    response_description="Topologie modifiée",
)
def update_topologie(
    topologie_id: int,
    data: TopologieUpdate,
    db: Session = Depends(get_db),
):

    topologie = (
        db.query(Topologie)
        .filter(
            Topologie.id == topologie_id
        )
        .first()
    )

    if not topologie:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topologie introuvable.",
        )

    if data.nom is not None:
        topologie.nom = data.nom

    if data.statut is not None:
        topologie.statut = data.statut

    db.commit()

    db.refresh(topologie)

    return topologie


# =============================================================================
# DELETE - SUPPRIMER UNE TOPOLOGIE
# =============================================================================

@router.delete(
    "/{topologie_id}",
    summary="Supprimer une topologie",
    description="""
    Supprime une topologie de la base de données.

    Les relations configurées avec les équipements et les connexions
    sont supprimées selon les règles de cascade définies dans les modèles.
    """,
    response_description="Confirmation de suppression",
)
def delete_topologie(
    topologie_id: int,
    db: Session = Depends(get_db),
):

    topologie = (
        db.query(Topologie)
        .filter(
            Topologie.id == topologie_id
        )
        .first()
    )

    if not topologie:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topologie introuvable.",
        )

    db.delete(topologie)

    db.commit()

    return {
        "message": "Topologie supprimée avec succès.",
        "topologie_id": topologie_id,
    }