import time

from fastapi import (
    APIRouter,
    HTTPException
)

from app.services.gns3_service import (
    GNS3Service
)

from app.services.yaml_service import (
    load_topology_yaml
)

from app.services.netmiko_service import (
    NetmikoService
)


# ==========================================================
# GENERATION DE LA CONFIGURATION DES ROUTEURS
# ==========================================================

def build_router_configuration(node):

    commands = []

    bootstrap = node.console_bootstrap


    # ======================================================
    # CONFIGURATION GENERALE
    # ======================================================

    if bootstrap:

        commands.extend(

            [

                f"hostname {bootstrap.hostname}",

                f"enable secret {bootstrap.enable_secret}",

                f"username {bootstrap.username} "
                f"privilege 15 secret {bootstrap.password}",

                "ip domain-name gns3.local",

            ]

        )


    # ======================================================
    # CONFIGURATION DES INTERFACES
    # ======================================================

    for interface in node.interfaces:

        interface_commands = [

            f"interface {interface.name}",

        ]


        if interface.description:

            interface_commands.append(

                f"description {interface.description}"

            )


        if interface.ip and interface.mask:

            interface_commands.append(

                f"ip address "
                f"{interface.ip} "
                f"{interface.mask}"

            )


        interface_commands.extend(

            [

                "no shutdown",

                "exit"

            ]

        )


        commands.extend(
            interface_commands
        )


    # ======================================================
    # CONFIGURATION SSH
    # ======================================================

    if bootstrap:

        commands.extend(

            [

                "crypto key generate rsa modulus 1024",

                "ip ssh version 2",

                "line vty 0 4",

                "login local",

                "transport input ssh",

                "exit",

            ]

        )


    # ======================================================
    # ROUTES STATIQUES
    # ======================================================

    for route in node.static_routes:

        commands.append(

            f"ip route "
            f"{route.network} "
            f"{route.mask} "
            f"{route.next_hop}"

        )


    return commands


# ==========================================================
# ROUTER FASTAPI
# ==========================================================

router = APIRouter(

    prefix="/api/topologies",

    tags=[
        "Deployment"
    ]

)


# ==========================================================
# DEPLOIEMENT YAML
# ==========================================================

@router.post(
    "/deploy-yaml"
)
def deploy_topology_from_yaml():

    try:


        # ==================================================
        # CHARGEMENT YAML
        # ==================================================

        topology = (
            load_topology_yaml()
        )


        # ==================================================
        # CONNEXION GNS3
        # ==================================================

        gns3 = (

            GNS3Service(

                host=(
                    topology
                    .gns3_server
                    .host
                ),

                port=(
                    topology
                    .gns3_server
                    .port
                ),

                protocol=(
                    topology
                    .gns3_server
                    .protocol
                ),

                user=(
                    topology
                    .gns3_server
                    .user
                ),

                password=(
                    topology
                    .gns3_server
                    .password
                ),

                compute_id=(
                    topology
                    .gns3_server
                    .compute_id
                )

            )

        )


        # ==================================================
        # VERIFICATION GNS3
        # ==================================================

        version = (
            gns3.get_version()
        )


        computes = (
            gns3.get_computes()
        )


        # ==================================================
        # PROJET
        # ==================================================

        project = (

            gns3.get_or_create_project(

                topology.project.name

            )

        )


        project_id = (
            project["project_id"]
        )


        gns3.open_project(
            project_id
        )


        # ==================================================
        # NETTOYAGE
        # ==================================================

        gns3.clear_project(
            project_id
        )

        time.sleep(2)


        # ==================================================
        # RESOLUTION DES TEMPLATES
        # ==================================================

        resolved_templates = {}


        templates_data = (

            topology
            .templates
            .model_dump()

        )


        for (
            template_key,
            template_name
        ) in templates_data.items():

            template = (

                gns3.find_template(
                    template_name
                )

            )


            resolved_templates[
                template_key
            ] = template


        # ==================================================
        # CREATION DES NODES
        # ==================================================

        created_nodes = {}

        nodes_created_response = []


        for node in topology.nodes:


            # ==============================================
            # CLOUD
            # ==============================================

            if node.template == "cloud":

                if not node.cloud_interface:

                    raise ValueError(

                        f"Le Cloud "
                        f"{node.name} "
                        f"n'a pas de cloud_interface"

                    )


                cloud_compute_id = (

                    node.compute_id

                    or

                    topology
                    .gns3_server
                    .compute_id

                )


                gns3.find_compute(
                    cloud_compute_id
                )


                created_node = (

                    gns3.create_cloud_node(

                        project_id=project_id,

                        name=node.name,

                        x=node.x,

                        y=node.y,

                        interface_name=(
                            node.cloud_interface
                        ),

                        compute_id=(
                            cloud_compute_id
                        )

                    )

                )


                template_name = "Cloud"

                node_type = "cloud"

                node_compute_id = (
                    cloud_compute_id
                )


            # ==============================================
            # AUTRES NODES
            # ==============================================

            else:

                template_key = (
                    node.template
                )


                if (

                    template_key

                    not in

                    resolved_templates

                ):

                    raise ValueError(

                        f"Template YAML inconnu : "
                        f"{template_key}"

                    )


                template = (

                    resolved_templates[
                        template_key
                    ]

                )


                node_compute_id = (

                    node.compute_id

                    or

                    topology
                    .gns3_server
                    .compute_id

                )


                gns3.find_compute(
                    node_compute_id
                )


                created_node = (

                    gns3.create_node(

                        project_id=project_id,

                        name=node.name,

                        x=node.x,

                        y=node.y,

                        template_id=(
                            template[
                                "template_id"
                            ]
                        ),

                        compute_id=(
                            node_compute_id
                        )

                    )

                )


                template_name = (
                    template["name"]
                )


                node_type = (

                    created_node.get(
                        "node_type"
                    )

                )


            # ==============================================
            # SAUVEGARDE NODE
            # ==============================================

            created_nodes[
                node.name
            ] = created_node


            nodes_created_response.append(

                {

                    "name":
                        node.name,

                    "node_id":
                        created_node.get(
                            "node_id"
                        ),

                    "template":
                        template_name,

                    "node_type":
                        node_type,

                    "compute_id":
                        node_compute_id

                }

            )


        # ==================================================
        # CREATION DES LIENS
        # ==================================================

        links_created_response = []


        for link in topology.links:


            if len(link.endpoints) != 2:

                raise ValueError(

                    "Chaque lien doit avoir "
                    "exactement 2 endpoints"

                )


            source = (
                link.endpoints[0]
            )

            destination = (
                link.endpoints[1]
            )


            if source.node not in created_nodes:

                raise ValueError(

                    f"Node source introuvable : "
                    f"{source.node}"

                )


            if destination.node not in created_nodes:

                raise ValueError(

                    f"Node destination introuvable : "
                    f"{destination.node}"

                )


            source_node = (
                created_nodes[
                    source.node
                ]
            )


            destination_node = (
                created_nodes[
                    destination.node
                ]
            )


            created_link = (

                gns3.create_link(

                    project_id=project_id,

                    node_source_id=(
                        source_node[
                            "node_id"
                        ]
                    ),

                    adapter_source=(
                        source.adapter
                    ),

                    port_source=(
                        source.port
                    ),

                    node_destination_id=(
                        destination_node[
                            "node_id"
                        ]
                    ),

                    adapter_destination=(
                        destination.adapter
                    ),

                    port_destination=(
                        destination.port
                    )

                )

            )


            links_created_response.append(

                {

                    "source": {

                        "node":
                            source.node,

                        "adapter":
                            source.adapter,

                        "port":
                            source.port

                    },

                    "destination": {

                        "node":
                            destination.node,

                        "adapter":
                            destination.adapter,

                        "port":
                            destination.port

                    },

                    "link_id":
                        created_link.get(
                            "link_id"
                        )

                }

            )


        # ==================================================
        # DEMARRAGE DES NODES
        # ==================================================

        nodes_started_response = []


        for node in topology.nodes:


            created_node = (
                created_nodes[
                    node.name
                ]
            )


            node_id = (
                created_node[
                    "node_id"
                ]
            )


            # ==============================================
            # CLOUD
            # ==============================================

            if node.template == "cloud":

                current_node = (

                    gns3.get_node(

                        project_id,

                        node_id

                    )

                )


                nodes_started_response.append(

                    {

                        "name":
                            node.name,

                        "node_id":
                            node_id,

                        "status":
                            current_node.get(
                                "status"
                            ),

                        "compute_id":
                            current_node.get(
                                "compute_id"
                            ),

                        "started":
                            False,

                        "message":
                            "Cloud créé, aucun démarrage nécessaire"

                    }

                )

                continue


            # ==============================================
            # AUTRES NODES
            # ==============================================

            gns3.start_node(

                project_id,

                node_id

            )


            time.sleep(2)


            current_node = (

                gns3.get_node(

                    project_id,

                    node_id

                )

            )


            nodes_started_response.append(

                {

                    "name":
                        node.name,

                    "node_id":
                        node_id,

                    "status":
                        current_node.get(
                            "status"
                        ),

                    "compute_id":
                        current_node.get(
                            "compute_id"
                        ),

                    "started":
                        True

                }

            )


        # ==================================================
        # ATTENTE DU BOOT DES ROUTEURS
        # ==================================================

        time.sleep(15)


        # ==================================================
        # BOOTSTRAP AUTOMATIQUE PAR CONSOLE GNS3
        # ==================================================

        console_bootstrap_results = []


        for node in topology.nodes:


            if node.template != "router":

                continue


            bootstrap = (
                node.console_bootstrap
            )


            if not bootstrap:

                console_bootstrap_results.append(

                    {

                        "router":
                            node.name,

                        "bootstrapped":
                            False,

                        "error":
                            "console_bootstrap absent"

                    }

                )

                continue


            console_netmiko = None


            try:


                # ==========================================
                # NODE GNS3
                # ==========================================

                created_node = (

                    created_nodes[
                        node.name
                    ]

                )


                node_id = (
                    created_node[
                        "node_id"
                    ]
                )


                # ==========================================
                # CONSOLE
                # ==========================================

                console = (

                    gns3.get_node_console(

                        project_id,

                        node_id

                    )

                )


                # ==========================================
                # COMMANDES
                # ==========================================

                commands = (

                    build_router_configuration(
                        node
                    )

                )


                # ==========================================
                # CONNEXION TELNET
                # ==========================================

                console_netmiko = (

                    NetmikoService(

                        host=(
                            console[
                                "host"
                            ]
                        ),

                        username=None,

                        password=None,

                        port=(
                            console[
                                "port"
                            ]
                        ),

                        device_type=(
                            "cisco_ios_telnet"
                        )

                    )

                )


                console_netmiko.connect_console(

                    console_host=(
                        console[
                            "host"
                        ]
                    ),

                    console_port=(
                        console[
                            "port"
                        ]
                    )

                )


                # ==========================================
                # ENVOI CONFIGURATION
                # ==========================================

                output = (

                    console_netmiko.bootstrap_configuration(
                        commands
                    )

                )


                # ==========================================
                # SAUVEGARDE
                # ==========================================

                console_netmiko.save_config()


                # ==========================================
                # DECONNEXION
                # ==========================================

                console_netmiko.disconnect()


                console_bootstrap_results.append(

                    {

                        "router":
                            node.name,

                        "console_host":
                            console[
                                "host"
                            ],

                        "console_port":
                            console[
                                "port"
                            ],

                        "bootstrapped":
                            True,

                        "commands_count":
                            len(
                                commands
                            ),

                        "output":
                            output

                    }

                )


            except Exception as console_error:


                if console_netmiko:

                    try:

                        console_netmiko.disconnect()

                    except Exception:

                        pass


                console_bootstrap_results.append(

                    {

                        "router":
                            node.name,

                        "bootstrapped":
                            False,

                        "error":
                            str(
                                console_error
                            )

                    }

                )


        # ==================================================
        # ATTENTE ACTIVATION SSH
        # ==================================================

        time.sleep(5)


        # ==================================================
        # VERIFICATION SSH AVEC NETMIKO
        # ==================================================

        netmiko_results = []


        for node in topology.nodes:


            if node.template != "router":

                continue


            bootstrap = (
                node.console_bootstrap
            )


            if not bootstrap:

                continue


            # ==============================================
            # RECHERCHE IP MANAGEMENT
            # ==============================================

            management_ip = None


            for interface in node.interfaces:


                if (

                    interface.ip

                    and

                    interface.ip.startswith(
                        "192.168.100."
                    )

                ):

                    management_ip = (
                        interface.ip
                    )

                    break


            if not management_ip:

                netmiko_results.append(

                    {

                        "router":
                            node.name,

                        "configured":
                            False,

                        "error":
                            "Adresse IP management introuvable"

                    }

                )

                continue


            ssh_netmiko = None


            try:


                # ==========================================
                # CONNEXION SSH
                # ==========================================

                ssh_netmiko = (

                    NetmikoService(

                        host=management_ip,

                        username=(
                            bootstrap.username
                        ),

                        password=(
                            bootstrap.password
                        ),

                        secret=(
                            bootstrap.enable_secret
                        )

                    )

                )


                ssh_netmiko.connect()


                # ==========================================
                # VERIFICATION
                # ==========================================

                verification = (

                    ssh_netmiko.send_commands(

                        [

                            "show ip interface brief",

                            "show ip ssh",

                            "show running-config"

                        ]

                    )

                )


                ssh_netmiko.disconnect()


                netmiko_results.append(

                    {

                        "router":
                            node.name,

                        "management_ip":
                            management_ip,

                        "configured":
                            True,

                        "verification":
                            verification

                    }

                )


            except Exception as netmiko_error:


                if ssh_netmiko:

                    try:

                        ssh_netmiko.disconnect()

                    except Exception:

                        pass


                netmiko_results.append(

                    {

                        "router":
                            node.name,

                        "management_ip":
                            management_ip,

                        "configured":
                            False,

                        "error":
                            str(
                                netmiko_error
                            )

                    }

                )


        # ==================================================
        # REPONSE FINALE
        # ==================================================

        return {

            "message":

                "Topologie déployée avec succès",


            "gns3_version":

                version,


            "computes":

                computes,


            "project": {

                "name":

                    project.get(
                        "name"
                    ),

                "project_id":

                    project_id

            },


            "nombre_nodes":

                len(
                    created_nodes
                ),


            "nombre_links":

                len(
                    links_created_response
                ),


            "nodes_created":

                nodes_created_response,


            "links_created":

                links_created_response,


            "nodes_started":

                nodes_started_response,


            # ==========================================
            # RESULTAT BOOTSTRAP CONSOLE
            # ==========================================

            "console_bootstrap":

                console_bootstrap_results,


            # ==========================================
            # RESULTAT VERIFICATION SSH
            # ==========================================

            "netmiko_configuration":

                netmiko_results

        }


    except Exception as error:


        raise HTTPException(

            status_code=500,

            detail=(

                "Erreur lors du "
                "déploiement GNS3 : "
                f"{str(error)}"

            )

        )