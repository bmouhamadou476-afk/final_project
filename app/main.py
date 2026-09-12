# =============================================================================
# APPLICATION PRINCIPALE
# Projet : Automatisation d'une topologie réseau avec FastAPI, GNS3 et Netmiko
# =============================================================================

from fastapi import FastAPI

from app.routes.topologies import router as topologies_router
from app.routes.equipements import router as equipements_router
from app.routes.interfaces import router as interfaces_router
from app.routes.connexions import router as connexions_router
from app.routes.deployment import router as deployment_router


# =============================================================================
# CONFIGURATION DE L'APPLICATION
# =============================================================================

app = FastAPI(
    title="Network Topology Automation API",

    description="""
# Network Topology Automation API

API REST permettant de gérer et d'automatiser une infrastructure
réseau virtuelle avec **FastAPI**, **MySQL**, **GNS3** et **Netmiko**.

---

## Architecture

L'application utilise :

- **FastAPI** : API REST et documentation OpenAPI
- **Pydantic** : validation des données
- **SQLAlchemy** : ORM
- **MySQL** : stockage des données
- **GNS3** : émulation de l'infrastructure réseau
- **Netmiko** : automatisation et configuration SSH des équipements

---

## Fonctionnement

Le fonctionnement général est le suivant :

1. Création d'une topologie.
2. Création des équipements.
3. Création des interfaces.
4. Création des connexions.
5. Déploiement automatique dans GNS3.
6. Démarrage automatique des équipements.
7. Connexion automatique à la console GNS3.
8. Configuration automatique des interfaces.
9. Configuration automatique de SSH.
10. Génération des clés RSA.
11. Connexion SSH avec Netmiko.
12. Vérification de la configuration réseau.

---

## Base de données

MySQL constitue la source de vérité de la topologie.

Les principales tables sont :

- `topologies`
- `equipements`
- `interfaces`
- `connexions`

---

## Déploiement

Le endpoint :

`POST /api/topologies/{topologie_id}/deploy`

permet de déployer automatiquement une topologie dans GNS3.

Le déploiement crée les équipements, les connexions,
démarre les équipements, configure leurs interfaces,
active SSH puis utilise Netmiko pour la connexion distante.

---

## Technologies

**FastAPI • Pydantic • SQLAlchemy • MySQL • GNS3 • Netmiko • SSH**
""",

    version="1.0.0",

    docs_url="/docs",

    redoc_url="/redoc",

    openapi_url="/openapi.json",
)


# =============================================================================
# ROUTES
# =============================================================================

app.include_router(
    topologies_router
)

app.include_router(
    equipements_router
)

app.include_router(
    interfaces_router
)

app.include_router(
    connexions_router
)

app.include_router(
    deployment_router
)


# =============================================================================
# ROUTE RACINE
# =============================================================================

@app.get(
    "/",
    tags=["Application"],
    summary="Informations sur l'API",
    description="""
    Retourne les informations générales sur l'API.

    Cette route permet de vérifier que l'application FastAPI
    fonctionne correctement.
    """,
    response_description="Informations générales de l'API",
)
def root():

    return {
        "application": "Network Topology Automation API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "redoc": "/redoc",
    }


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get(
    "/health",
    tags=["Application"],
    summary="Vérifier l'état de l'API",
    description="""
    Vérifie que l'API est disponible et opérationnelle.

    Cette route peut également être utilisée comme endpoint
    de health check lors de la conteneurisation Docker.
    """,
    response_description="État de fonctionnement de l'API",
)
def health_check():

    return {
        "status": "healthy",
        "service": "network-automation",
    }