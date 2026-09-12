from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.databases import Base


class Topologie(Base):

    __tablename__ = "topologies"

    # =========================================================
    # IDENTIFICATION
    # =========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    nom = Column(
        String(150),
        nullable=False,
        unique=True,
    )

    # =========================================================
    # GNS3
    # =========================================================

    gns3_project_id = Column(
        String(100),
        nullable=True,
        unique=True,
    )

    # =========================================================
    # ÉTAT
    # =========================================================

    statut = Column(
        String(50),
        nullable=False,
        default="created",
    )

    date_creation = Column(
        DateTime,
        server_default=func.now(),
    )

    # =========================================================
    # RELATION ÉQUIPEMENTS
    # =========================================================

    equipements = relationship(
        "Equipement",
        back_populates="topologie",
        cascade="all, delete-orphan",
    )

    # =========================================================
    # RELATION CONNEXIONS
    # =========================================================

    connexions = relationship(
        "Connexion",
        back_populates="topologie",
        cascade="all, delete-orphan",
    )