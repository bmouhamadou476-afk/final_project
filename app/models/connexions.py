from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.databases import Base


class Connexion(Base):

    __tablename__ = "connexions"

    # =========================================================
    # IDENTIFICATION
    # =========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # =========================================================
    # GNS3
    # =========================================================

    gns3_link_id = Column(
        String(100),
        nullable=True,
        unique=True,
    )

    # =========================================================
    # SOURCE
    # =========================================================

    equipement_source_id = Column(
        Integer,
        ForeignKey("equipements.id"),
        nullable=False,
    )

    interface_source_id = Column(
        Integer,
        ForeignKey("interfaces.id"),
        nullable=False,
    )

    # =========================================================
    # DESTINATION
    # =========================================================

    equipement_destination_id = Column(
        Integer,
        ForeignKey("equipements.id"),
        nullable=False,
    )

    interface_destination_id = Column(
        Integer,
        ForeignKey("interfaces.id"),
        nullable=False,
    )

    # =========================================================
    # TOPOLOGIE
    # =========================================================

    topologie_id = Column(
        Integer,
        ForeignKey("topologies.id"),
        nullable=False,
    )

    # =========================================================
    # RELATIONS
    # =========================================================

    topologie = relationship(
        "Topologie",
        back_populates="connexions",
    )

    equipement_source = relationship(
        "Equipement",
        foreign_keys=[equipement_source_id],
    )

    interface_source = relationship(
        "Interface",
        foreign_keys=[interface_source_id],
    )

    equipement_destination = relationship(
        "Equipement",
        foreign_keys=[equipement_destination_id],
    )

    interface_destination = relationship(
        "Interface",
        foreign_keys=[interface_destination_id],
    )