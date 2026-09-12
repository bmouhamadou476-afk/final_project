from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.databases import Base


class Equipement(Base):

    __tablename__ = "equipements"

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

    type_equipement = Column(
        String(50),
        nullable=False,
        default="routeur",
    )

    # =========================================================
    # GNS3
    # =========================================================

    template_gns3 = Column(
        String(100),
        nullable=False,
    )

    compute_id = Column(
        String(100),
        nullable=False,
        default="local",
    )

    gns3_node_id = Column(
        String(100),
        nullable=True,
        unique=True,
    )

    # Position du nœud dans GNS3
    x = Column(
        Integer,
        nullable=True,
    )

    y = Column(
        Integer,
        nullable=True,
    )

    # =========================================================
    # MANAGEMENT / SSH
    # =========================================================

    adresse_ip = Column(
        String(50),
        nullable=True,
    )

    management_ip = Column(
        String(50),
        nullable=True,
    )

    username = Column(
        String(100),
        nullable=True,
    )

    password = Column(
        String(255),
        nullable=True,
    )

    enable_secret = Column(
        String(255),
        nullable=True,
    )

    # =========================================================
    # ÉTAT
    # =========================================================

    actif = Column(
        Boolean,
        default=False,
    )

    # =========================================================
    # TOPOLOGIE
    # =========================================================

    topologie_id = Column(
        Integer,
        ForeignKey("topologies.id"),
        nullable=False,
    )

    topologie = relationship(
        "Topologie",
        back_populates="equipements",
    )

    # =========================================================
    # INTERFACES
    # =========================================================

    interfaces = relationship(
        "Interface",
        back_populates="equipement",
        cascade="all, delete-orphan",
    )