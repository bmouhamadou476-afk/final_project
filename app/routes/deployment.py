# =============================================================================
# ÉTAPE 1 - IMPORTS
# =============================================================================

import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.databases import get_db

from app.models.topology import Topologie
from app.models.equipements import Equipement
from app.models.interfaces import Interface
from app.models.connexions import Connexion

from app.services.gns3_service import GNS3Service
from app.services.netmiko_service import NetmikoService


# =============================================================================
# ÉTAPE 2 - ROUTER FASTAPI
# =============================================================================

router = APIRouter(
    prefix="/api/topologies",
    tags=["Deployment"],
)


# =============================================================================
# ÉTAPE 3 - CONSTRUCTION DE LA CONFIGURATION INTERFACE
# =============================================================================

def build_interface_commands(interfaces):
    """
    Construit automatiquement les commandes Cisco
    à partir des interfaces enregistrées dans MySQL.
    """

    commands = []

    for interface in interfaces:

        # Une interface sans adresse IP ne nécessite
        # pas de configuration IP.
        if not interface.adresse_ip:
            continue

        if not interface.masque:
            continue

        commands.append(
            f"interface {interface.nom}"
        )

        commands.append(
            f"ip address {interface.adresse_ip} "
            f"{interface.masque}"
        )

        commands.append(
            "no shutdown"
        )

        if interface.description:
            commands.append(
                f"description {interface.description}"
            )

        commands.append("exit")

    return commands


# =============================================================================
# ÉTAPE 4 - CONSTRUCTION DE LA CONFIGURATION SSH
# =============================================================================

def build_ssh_commands(equipement):
    """
    Construit automatiquement la configuration SSH
    à partir des informations de l'équipement.
    """

    commands = []

    if equipement.username and equipement.password:

        commands.append(
            f"username {equipement.username} "
            f"privilege 15 "
            f"secret {equipement.password}"
        )

    # Nécessaire pour la génération des clés RSA
    commands.append(
        "ip domain-name lab.local"
    )

    commands.append(
        "ip ssh version 2"
    )

    # Configuration des lignes VTY
    commands.append(
        "line vty 0 4"
    )

    commands.append(
        "login local"
    )

    commands.append(
        "transport input ssh"
    )

    commands.append(
        "exit"
    )

    return commands


# =============================================================================
# ÉTAPE 5 - DEPLOIEMENT COMPLET
# =============================================================================

@router.post(
    "/{topologie_id}/deploy",

    summary="Déployer automatiquement une topologie",

    description="""
    # Déploiement automatique d'une topologie réseau

    Déploie une topologie enregistrée dans MySQL vers GNS3.

    ## Étapes du déploiement

    Le processus automatique réalise les opérations suivantes :

    1. Récupération de la topologie depuis MySQL.
    2. Création ou récupération du projet GNS3.
    3. Création des équipements dans GNS3.
    4. Création des connexions entre les équipements.
    5. Démarrage automatique des équipements.
    6. Attente de la disponibilité des consoles.
    7. Connexion automatique aux consoles GNS3.
    8. Configuration des interfaces réseau.
    9. Configuration des utilisateurs SSH.
    10. Configuration des lignes VTY.
    11. Génération des clés RSA.
    12. Sauvegarde de la configuration.
    13. Attente de la disponibilité du service SSH.
    14. Connexion automatique avec Netmiko.
    15. Vérification des interfaces et de la configuration.

    ## Source des données

    MySQL constitue la source de vérité.

    Les équipements sont récupérés depuis la table `equipements`,
    les interfaces depuis `interfaces` et les connexions depuis
    `connexions`.

    ## GNS3

    Les équipements sont automatiquement créés dans le projet GNS3
    correspondant à la topologie.

    ## SSH / Netmiko

    Une fois l'adresse IP de management configurée par la console,
    l'application établit automatiquement une connexion SSH avec
    Netmiko.

    ## Résultat

    Le endpoint retourne :

    - les informations du projet GNS3 ;
    - les équipements créés ;
    - les connexions créées ;
    - la configuration des interfaces ;
    - la configuration SSH ;
    - les vérifications SSH ;
    - les éventuelles erreurs.
    """,

    response_description=(
        "Résultat détaillé du déploiement "
        "de la topologie"
    ),

    responses={
        200: {
            "description": (
                "Topologie déployée avec succès "
                "ou avec des erreurs partielles."
            )
        },
        400: {
            "description": (
                "La topologie ne peut pas être déployée."
            )
        },
        404: {
            "description": (
                "Topologie introuvable."
            )
        },
        500: {
            "description": (
                "Erreur interne pendant le déploiement."
            )
        },
    },
)
def deploy_topologie(
    topologie_id: int,
    db: Session = Depends(get_db),
):

    # -------------------------------------------------------------------------
    # 5.1 - Récupération de la topologie
    # -------------------------------------------------------------------------

    topologie = (
        db.query(Topologie)
        .filter(
            Topologie.id == topologie_id
        )
        .first()
    )

    if not topologie:
        raise HTTPException(
            status_code=404,
            detail="Topologie introuvable"
        )

    # -------------------------------------------------------------------------
    # 5.2 - Récupération des équipements
    # -------------------------------------------------------------------------

    equipements = (
        db.query(Equipement)
        .filter(
            Equipement.topologie_id == topologie_id
        )
        .all()
    )

    if not equipements:
        raise HTTPException(
            status_code=400,
            detail="La topologie ne contient aucun équipement"
        )

    # -------------------------------------------------------------------------
    # 5.3 - Récupération des connexions
    # -------------------------------------------------------------------------

    connexions = (
        db.query(Connexion)
        .filter(
            Connexion.topologie_id == topologie_id
        )
        .all()
    )

    # -------------------------------------------------------------------------
    # 5.4 - Initialisation GNS3
    # -------------------------------------------------------------------------

    gns3 = GNS3Service()

    result = {
        "topologie": {
            "id": topologie.id,
            "nom": topologie.nom,
            "statut": None,
        },

        "gns3": {
            "project_id": None,
        },

        "equipements": [],

        "connexions": [],

        "configuration_interfaces": [],

        "configuration_ssh": [],

        "verification_ssh": [],

        "erreurs": [],
    }

    try:

        # =====================================================================
        # ÉTAPE 6 - CRÉATION / RÉCUPÉRATION DU PROJET GNS3
        # =====================================================================

        project = gns3.get_or_create_project(
            topologie.nom
        )

        project_id = project.get(
            "project_id"
        )

        if not project_id:
            raise ValueError(
                "GNS3 n'a pas retourné de project_id."
            )

        result["gns3"]["project_id"] = project_id

        topologie.gns3_project_id = project_id

        topologie.statut = "deploying"

        db.commit()

        # =====================================================================
        # ÉTAPE 7 - OUVERTURE ET NETTOYAGE DU PROJET GNS3
        # =====================================================================

        gns3.open_project(
            project_id
        )

        gns3.clear_project(
            project_id
        )

        # Dictionnaire :
        #
        # ID MySQL équipement
        #        ↓
        # ID node GNS3
        #
        node_map = {}

        # =====================================================================
        # ÉTAPE 8 - CRÉATION AUTOMATIQUE DES ÉQUIPEMENTS GNS3
        # =====================================================================

        for equipement in equipements:

            if not equipement.template_gns3:

                raise ValueError(
                    f"L'équipement {equipement.nom} "
                    "n'a pas de template GNS3."
                )

            # -----------------------------------------------------------------
            # Recherche du template
            # -----------------------------------------------------------------

            template = gns3.find_template(
                equipement.template_gns3
            )

            template_id = template.get(
                "template_id"
            )

            if not template_id:

                raise ValueError(
                    f"Le template "
                    f"{equipement.template_gns3} "
                    "ne possède pas de template_id."
                )

            # -----------------------------------------------------------------
            # Paramètres GNS3
            # -----------------------------------------------------------------

            compute_id = (
                equipement.compute_id
                or "local"
            )

            x = (
                equipement.x
                if equipement.x is not None
                else 100
            )

            y = (
                equipement.y
                if equipement.y is not None
                else 100
            )

            # -----------------------------------------------------------------
            # Création du node
            # -----------------------------------------------------------------

            node = gns3.create_node(
                project_id=project_id,
                template_id=template_id,
                compute_id=compute_id,
                name=equipement.nom,
                x=x,
                y=y,
            )

            node_id = node.get(
                "node_id"
            )

            if not node_id:

                raise ValueError(
                    f"GNS3 n'a pas retourné de node_id "
                    f"pour {equipement.nom}."
                )

            # -----------------------------------------------------------------
            # Sauvegarde de l'ID GNS3 dans MySQL
            # -----------------------------------------------------------------

            equipement.gns3_node_id = node_id

            db.commit()

            node_map[equipement.id] = node_id

            result["equipements"].append(
                {
                    "id": equipement.id,
                    "nom": equipement.nom,
                    "template": equipement.template_gns3,
                    "compute_id": compute_id,
                    "gns3_node_id": node_id,
                }
            )

        # =====================================================================
        # ÉTAPE 9 - CRÉATION AUTOMATIQUE DES CONNEXIONS GNS3
        # =====================================================================

        for connexion in connexions:

            source_node_id = node_map.get(
                connexion.equipement_source_id
            )

            destination_node_id = node_map.get(
                connexion.equipement_destination_id
            )

            if not source_node_id:

                raise ValueError(
                    "Node GNS3 source introuvable "
                    f"pour l'équipement "
                    f"{connexion.equipement_source_id}."
                )

            if not destination_node_id:

                raise ValueError(
                    "Node GNS3 destination introuvable "
                    f"pour l'équipement "
                    f"{connexion.equipement_destination_id}."
                )

            # -----------------------------------------------------------------
            # Interface source
            # -----------------------------------------------------------------

            interface_source = (
                db.query(Interface)
                .filter(
                    Interface.id
                    == connexion.interface_source_id
                )
                .first()
            )

            if not interface_source:

                raise ValueError(
                    "Interface source introuvable "
                    f"(ID={connexion.interface_source_id})."
                )

            # -----------------------------------------------------------------
            # Interface destination
            # -----------------------------------------------------------------

            interface_destination = (
                db.query(Interface)
                .filter(
                    Interface.id
                    == connexion.interface_destination_id
                )
                .first()
            )

            if not interface_destination:

                raise ValueError(
                    "Interface destination introuvable "
                    f"(ID={connexion.interface_destination_id})."
                )

            # -----------------------------------------------------------------
            # Vérification propriétaire interface source
            # -----------------------------------------------------------------

            if (
                interface_source.equipement_id
                != connexion.equipement_source_id
            ):

                raise ValueError(
                    f"L'interface "
                    f"{interface_source.id} "
                    "n'appartient pas à "
                    "l'équipement source."
                )

            # -----------------------------------------------------------------
            # Vérification propriétaire interface destination
            # -----------------------------------------------------------------

            if (
                interface_destination.equipement_id
                != connexion.equipement_destination_id
            ):

                raise ValueError(
                    f"L'interface "
                    f"{interface_destination.id} "
                    "n'appartient pas à "
                    "l'équipement destination."
                )

            # -----------------------------------------------------------------
            # Création du lien GNS3
            # -----------------------------------------------------------------

            link = gns3.create_link(
                project_id=project_id,

                node_source_id=source_node_id,
                adapter_source=interface_source.adapter,
                port_source=interface_source.port,

                node_destination_id=destination_node_id,
                adapter_destination=interface_destination.adapter,
                port_destination=interface_destination.port,
            )

            link_id = link.get(
                "link_id"
            )

            connexion.gns3_link_id = link_id

            db.commit()

            result["connexions"].append(
                {
                    "connexion_id": connexion.id,
                    "gns3_link_id": link_id,

                    "source": {
                        "equipement_id":
                            connexion.equipement_source_id,
                        "interface_id":
                            connexion.interface_source_id,
                    },

                    "destination": {
                        "equipement_id":
                            connexion.equipement_destination_id,
                        "interface_id":
                            connexion.interface_destination_id,
                    },
                }
            )

        # =====================================================================
        # ÉTAPE 10 - DÉMARRAGE AUTOMATIQUE DES ÉQUIPEMENTS
        # =====================================================================

        for equipement in equipements:

            node_id = node_map.get(
                equipement.id
            )

            if not node_id:
                continue

            try:

                # -------------------------------------------------------------
                # Démarrage
                # -------------------------------------------------------------

                gns3.start_node(
                    project_id,
                    node_id
                )

                # -------------------------------------------------------------
                # Attente du démarrage
                # -------------------------------------------------------------

                gns3.wait_for_node_started(
                    project_id,
                    node_id,
                    timeout=120,
                    interval=3,
                )

                equipement.actif = True

                db.commit()

            except Exception as error:

                result["erreurs"].append(
                    {
                        "equipement":
                            equipement.nom,

                        "etape":
                            "demarrage",

                        "erreur":
                            str(error),
                    }
                )

        # =====================================================================
        # ÉTAPE 11 - ATTENTE DES CONSOLES
        # =====================================================================

        time.sleep(3)

        # =====================================================================
        # ÉTAPE 12 - CONFIGURATION AUTOMATIQUE PAR CONSOLE
        #
        # C'est ici que nous configurons les interfaces AVANT SSH.
        # =====================================================================

        for equipement in equipements:

            node_id = node_map.get(
                equipement.id
            )

            if not node_id:
                continue

            try:

                # -------------------------------------------------------------
                # Attente de la console GNS3
                # -------------------------------------------------------------

                console = gns3.wait_for_console(
                    project_id,
                    node_id,
                    timeout=120,
                    interval=3,
                )

                console_host = (
                    console.get("host")
                    or "127.0.0.1"
                )

                console_port = console.get(
                    "port"
                )

                if not console_port:

                    raise ValueError(
                        "Port console GNS3 introuvable."
                    )

                # -------------------------------------------------------------
                # Connexion console Netmiko
                # -------------------------------------------------------------

                netmiko = NetmikoService(
                    host=console_host,
                    port=console_port,
                )

                netmiko.connect_console(
                    console_host,
                    console_port,
                    max_attempts=10,
                    delay=5,
                )

                # -------------------------------------------------------------
                # Préparation de la console
                # -------------------------------------------------------------

                netmiko.prepare_console()

                # -------------------------------------------------------------
                # Récupération des interfaces MySQL
                # -------------------------------------------------------------

                interfaces = (
                    db.query(Interface)
                    .filter(
                        Interface.equipement_id
                        == equipement.id
                    )
                    .all()
                )

                # -------------------------------------------------------------
                # Construction automatique des commandes interfaces
                # -------------------------------------------------------------

                interface_commands = (
                    build_interface_commands(
                        interfaces
                    )
                )

                # -------------------------------------------------------------
                # Configuration interfaces
                # -------------------------------------------------------------

                if interface_commands:

                    netmiko.send_config(
                        interface_commands
                    )

                # -------------------------------------------------------------
                # Configuration SSH
                # -------------------------------------------------------------

                ssh_commands = (
                    build_ssh_commands(
                        equipement
                    )
                )

                if ssh_commands:

                    netmiko.send_config(
                        ssh_commands
                    )

                # -------------------------------------------------------------
                # Génération automatique des clés RSA
                # -------------------------------------------------------------

                if (
                    equipement.username
                    and equipement.password
                ):

                    netmiko.generate_rsa_keys(
                        modulus=1024
                    )

                # -------------------------------------------------------------
                # Sauvegarde
                # -------------------------------------------------------------

                netmiko.save_config()

                # -------------------------------------------------------------
                # Vérification console
                # -------------------------------------------------------------

                interface_output = (
                    netmiko.send_command(
                        "show ip interface brief"
                    )
                )

                # -------------------------------------------------------------
                # Déconnexion console
                # -------------------------------------------------------------

                netmiko.disconnect()

                # -------------------------------------------------------------
                # Résultat
                # -------------------------------------------------------------

                result[
                    "configuration_interfaces"
                ].append(
                    {
                        "equipement":
                            equipement.nom,

                        "status":
                            "success",

                        "interfaces_configurees":
                            len(interface_commands),

                        "verification":
                            interface_output,
                    }
                )

                result[
                    "configuration_ssh"
                ].append(
                    {
                        "equipement":
                            equipement.nom,

                        "status":
                            "configured",
                    }
                )

            except Exception as error:

                result["erreurs"].append(
                    {
                        "equipement":
                            equipement.nom,

                        "etape":
                            "configuration_console",

                        "erreur":
                            str(error),
                    }
                )

        # =====================================================================
        # ÉTAPE 13 - ATTENTE DU DÉMARRAGE DU SERVICE SSH
        # =====================================================================

        time.sleep(10)

        # =====================================================================
        # ÉTAPE 14 - CONNEXION SSH AUTOMATIQUE AVEC NETMIKO
        # =====================================================================

        for equipement in equipements:

            # -----------------------------------------------------------------
            # Il faut une IP de management
            # -----------------------------------------------------------------

            if not equipement.management_ip:

                result["erreurs"].append(
                    {
                        "equipement":
                            equipement.nom,

                        "etape":
                            "ssh",

                        "erreur":
                            "Aucune management_ip définie.",
                    }
                )

                continue

            # -----------------------------------------------------------------
            # Identifiants SSH
            # -----------------------------------------------------------------

            if not equipement.username:

                result["erreurs"].append(
                    {
                        "equipement":
                            equipement.nom,

                        "etape":
                            "ssh",

                        "erreur":
                            "Aucun username SSH défini.",
                    }
                )

                continue

            if not equipement.password:

                result["erreurs"].append(
                    {
                        "equipement":
                            equipement.nom,

                        "etape":
                            "ssh",

                        "erreur":
                            "Aucun password SSH défini.",
                    }
                )

                continue

            try:

                # -------------------------------------------------------------
                # Création Netmiko SSH
                # -------------------------------------------------------------

                netmiko = NetmikoService(
                    host=equipement.management_ip,

                    username=equipement.username,

                    password=equipement.password,

                    secret=equipement.enable_secret,

                    device_type="cisco_ios",

                    port=22,
                )

                # -------------------------------------------------------------
                # Connexion SSH
                # -------------------------------------------------------------

                netmiko.connect(
                    max_attempts=10,
                    delay=10,
                )

                # -------------------------------------------------------------
                # Vérification SSH
                # -------------------------------------------------------------

                hostname = netmiko.send_command(
                    "show running-config | include hostname"
                )

                interfaces = netmiko.send_command(
                    "show ip interface brief"
                )

                # -------------------------------------------------------------
                # Sauvegarde
                # -------------------------------------------------------------

                netmiko.save_config()

                # -------------------------------------------------------------
                # Déconnexion
                # -------------------------------------------------------------

                netmiko.disconnect()

                # -------------------------------------------------------------
                # Résultat SSH
                # -------------------------------------------------------------

                result[
                    "verification_ssh"
                ].append(
                    {
                        "equipement":
                            equipement.nom,

                        "management_ip":
                            equipement.management_ip,

                        "status":
                            "success",

                        "hostname":
                            hostname,

                        "interfaces":
                            interfaces,
                    }
                )

            except Exception as error:

                result["erreurs"].append(
                    {
                        "equipement":
                            equipement.nom,

                        "etape":
                            "ssh",

                        "management_ip":
                            equipement.management_ip,

                        "erreur":
                            str(error),
                    }
                )

        # =====================================================================
        # ÉTAPE 15 - STATUT FINAL
        # =====================================================================

        if result["erreurs"]:

            topologie.statut = (
                "deployed_with_errors"
            )

        else:

            topologie.statut = (
                "deployed"
            )

        db.commit()

        result[
            "topologie"
        ]["statut"] = topologie.statut

        return result

    # =========================================================================
    # ÉTAPE 16 - GESTION DES ERREURS
    # =========================================================================

    except HTTPException:

        topologie.statut = "error"

        db.commit()

        raise

    except Exception as error:

        topologie.statut = "error"

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=(
                "Erreur pendant le déploiement : "
                f"{str(error)}"
            ),
        )