from fastapi import FastAPI
from app.routes.deployment import router as deployment_router
from app.routes.topologies import router as topologies_router
from app.routes.equipements import router as equipements_router
from app.routes.interfaces import router as interfaces_router
from app.routes.connexions import router as connexions_router


app = FastAPI(
    title="Network Topology Automation API",
    version="1.0.0"
)

app.include_router(deployment_router)
app.include_router(topologies_router)
app.include_router(equipements_router)
app.include_router(interfaces_router)
app.include_router(connexions_router)