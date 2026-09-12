from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.databases import Base


class Interface(Base):

    __tablename__ = "interfaces"

    # =========================================================
    # IDENTIFICATION
    # =========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    nom = Column(
        String(100),
        nullable=False,
    )

    # =========================================================
    # CONFIGURATION IP
    # =========================================================

    adresse_ip = Column(
        String(50),
        nullable=True,
    )

    masque = Column(
        String(50),
        nullable=True,
    )

    description = Column(
        String(255),
        nullable=True,
    )

    # =========================================================
    # GNS3
    # =========================================================

    adapter = Column(
        Integer,
        nullable=False,
    )

    port = Column(
        Integer,
        nullable=False,
    )

    # =========================================================
    # ÉQUIPEMENT
    # =========================================================

    equipement_id = Column(
        Integer,
        ForeignKey("equipements.id"),
        nullable=False,
    )

    equipement = relationship(
        "Equipement",
        back_populates="interfaces",
    )