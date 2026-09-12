from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)


# ==================================================
# CONFIGURATION PYDANTIC
# ==================================================

class BaseSchema(BaseModel):

    model_config = ConfigDict(
        populate_by_name=True
    )


# ==================================================
# PROJET
# ==================================================

class ProjectYAML(
    BaseSchema
):

    name: str


# ==================================================
# SERVEUR GNS3
# ==================================================

class GNS3ServerYAML(
    BaseSchema
):

    host: str

    port: int = 3080

    protocol: str = "http"

    user: Optional[str] = None

    password: Optional[str] = None

    compute_id: str = "local"


# ==================================================
# TEMPLATES
# ==================================================

class TemplatesYAML(
    BaseSchema
):

    router: str

    switch: str

    pc: str


# ==================================================
# CONSOLE / BOOTSTRAP ROUTEUR
# ==================================================

class ConsoleBootstrapYAML(
    BaseSchema
):

    hostname: str

    username: str

    password: str

    enable_secret: str


# ==================================================
# INTERFACES
# ==================================================

class InterfaceYAML(
    BaseSchema
):

    name: str

    adapter: int

    port: int

    ip: str

    mask: str

    description: Optional[str] = None


# ==================================================
# ROUTES STATIQUES
# ==================================================

class StaticRouteYAML(
    BaseSchema
):

    network: str

    mask: str

    next_hop: str


# ==================================================
# CONFIGURATION VPCS
# ==================================================

class VPCSConfigYAML(
    BaseSchema
):

    ip: str

    mask: str

    gateway: str


# ==================================================
# NODE
# ==================================================

class NodeYAML(
    BaseSchema
):

    name: str

    template: str

    x: int

    y: int

    # ----------------------------------------------
    # COMPUTE SPECIFIQUE AU NODE
    # Exemple :
    # compute_id: "vm"
    # ----------------------------------------------

    compute_id: Optional[str] = None


    # ----------------------------------------------
    # CLOUD
    # Exemple :
    # cloud_interface: "eth1"
    # ----------------------------------------------

    cloud_interface: Optional[str] = None


    # ----------------------------------------------
    # ROUTEUR
    # ----------------------------------------------

    console_bootstrap: Optional[
        ConsoleBootstrapYAML
    ] = None


    interfaces: list[
        InterfaceYAML
    ] = Field(
        default_factory=list
    )


    static_routes: list[
        StaticRouteYAML
    ] = Field(
        default_factory=list
    )


    # ----------------------------------------------
    # VPCS
    # ----------------------------------------------

    vpcs_config: Optional[
        VPCSConfigYAML
    ] = None


# ==================================================
# ENDPOINT D'UN LIEN
# ==================================================

class LinkEndpointYAML(
    BaseSchema
):

    node: str

    adapter: int

    port: int


# ==================================================
# LIEN
# ==================================================

class LinkYAML(
    BaseSchema
):

    endpoints: list[
        LinkEndpointYAML
    ]


# ==================================================
# TEST PING
# ==================================================

class PingTestYAML(
    BaseSchema
):

    # "from" est un mot réservé Python.
    # On utilise donc from_ en Python
    # et "from" dans le YAML.

    from_: str = Field(
        alias="from"
    )

    target: str

    description: Optional[str] = None


# ==================================================
# TESTS
# ==================================================

class TestsYAML(
    BaseSchema
):

    ping: list[
        PingTestYAML
    ] = Field(
        default_factory=list
    )


    show_commands: list[
        str
    ] = Field(
        default_factory=list
    )


# ==================================================
# TOPOLOGIE COMPLETE
# ==================================================

class TopologyYAML(
    BaseSchema
):

    project: ProjectYAML

    gns3_server: GNS3ServerYAML

    templates: TemplatesYAML

    nodes: list[
        NodeYAML
    ]

    links: list[
        LinkYAML
    ]

    tests: TestsYAML