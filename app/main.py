from fastapi import FastAPI

from app.routes.deployment import (
    router as deployment_router
)


app = FastAPI(
    title="API Gestion Topologies Réseau"
)


app.include_router(
    deployment_router
)