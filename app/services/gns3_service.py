import time

import requests


class GNS3Service:

    def __init__(
        self,
        host="127.0.0.1",
        port=3080,
        protocol="http",
        user=None,
        password=None,
        compute_id="local",
    ):
        self.base_url = f"{protocol}://{host}:{port}"
        self.compute_id = compute_id

        self.session = requests.Session()

        if user and password:
            self.session.auth = (
                user,
                password,
            )

    # ============================================================
    # REQUÊTE HTTP GÉNÉRIQUE
    # ============================================================

    def _request(
        self,
        method,
        url,
        **kwargs,
    ):
        response = self.session.request(
            method=method,
            url=url,
            timeout=60,
            **kwargs,
        )

        if not response.ok:

            try:
                error_data = response.json()
            except Exception:
                error_data = response.text

            raise ValueError(
                f"Erreur GNS3. "
                f"Status={response.status_code}, "
                f"URL={url}, "
                f"Reponse={error_data}"
            )

        if not response.content:
            return {}

        try:
            return response.json()
        except ValueError:
            return {}

    # ============================================================
    # VERSION GNS3
    # ============================================================

    def get_version(self):

        url = f"{self.base_url}/v2/version"

        return self._request(
            "GET",
            url,
        )

    # ============================================================
    # COMPUTES
    # ============================================================

    def get_computes(self):

        url = f"{self.base_url}/v2/computes"

        return self._request(
            "GET",
            url,
        )

    def find_compute(
        self,
        compute_id=None,
    ):

        if compute_id is None:
            compute_id = self.compute_id

        computes = self.get_computes()

        for compute in computes:

            if compute.get("compute_id") == compute_id:
                return compute

        available = [
            compute.get("compute_id")
            for compute in computes
        ]

        raise ValueError(
            f"Compute introuvable : {compute_id}. "
            f"Computes disponibles : {available}"
        )

    # ============================================================
    # TEMPLATES
    # ============================================================

    def get_templates(self):

        url = f"{self.base_url}/v2/templates"

        return self._request(
            "GET",
            url,
        )

    def find_template(
        self,
        template_name,
    ):

        if not template_name:
            raise ValueError(
                "Le nom du template GNS3 est vide."
            )

        templates = self.get_templates()

        requested_name = (
            str(template_name)
            .strip()
            .lower()
        )

        for template in templates:

            current_name = (
                template.get("name", "")
                .strip()
                .lower()
            )

            if current_name == requested_name:
                return template

        available = [
            template.get("name")
            for template in templates
        ]

        raise ValueError(
            f"Template introuvable : "
            f"{template_name}. "
            f"Templates disponibles : "
            f"{available}"
        )

    # ============================================================
    # PROJETS
    # ============================================================

    def get_projects(self):

        url = f"{self.base_url}/v2/projects"

        return self._request(
            "GET",
            url,
        )

    def create_project(
        self,
        project_name,
    ):

        if not project_name:
            raise ValueError(
                "Le nom du projet GNS3 est vide."
            )

        url = f"{self.base_url}/v2/projects"

        data = {
            "name": project_name,
        }

        return self._request(
            "POST",
            url,
            json=data,
        )

    def get_or_create_project(
        self,
        project_name,
    ):

        projects = self.get_projects()

        for project in projects:

            if project.get("name") == project_name:
                return project

        return self.create_project(
            project_name
        )

    def open_project(
        self,
        project_id,
    ):

        url = (
            f"{self.base_url}/v2/projects/"
            f"{project_id}/open"
        )

        return self._request(
            "POST",
            url,
        )

    # ============================================================
    # NŒUDS
    # ============================================================

    def get_nodes(
        self,
        project_id,
    ):

        url = (
            f"{self.base_url}/v2/projects/"
            f"{project_id}/nodes"
        )

        return self._request(
            "GET",
            url,
        )

    def get_node(
        self,
        project_id,
        node_id,
    ):

        url = (
            f"{self.base_url}/v2/projects/"
            f"{project_id}/nodes/"
            f"{node_id}"
        )

        return self._request(
            "GET",
            url,
        )

    # ============================================================
    # SUPPRIMER UN NŒUD
    # ============================================================

    def delete_node(
        self,
        project_id,
        node_id,
    ):

        url = (
            f"{self.base_url}/v2/projects/"
            f"{project_id}/nodes/"
            f"{node_id}"
        )

        return self._request(
            "DELETE",
            url,
        )

    # ============================================================
    # NETTOYER LE PROJET
    # ============================================================

    def clear_project(
        self,
        project_id,
    ):

        nodes = self.get_nodes(
            project_id
        )

        deleted = []

        for node in nodes:

            node_id = node.get("node_id")
            node_name = node.get("name")
            node_type = node.get("node_type")

            if not node_id:
                continue

            # Arrêter avant suppression
            if node_type != "cloud":

                try:
                    self.stop_node(
                        project_id,
                        node_id,
                    )
                except Exception:
                    pass

            try:

                self.delete_node(
                    project_id,
                    node_id,
                )

                deleted.append(
                    {
                        "id": node_id,
                        "name": node_name,
                        "node_type": node_type,
                    }
                )

            except Exception as error:

                raise ValueError(
                    f"Impossible de supprimer "
                    f"le nœud {node_name} : "
                    f"{error}"
                )

        return deleted

    # ============================================================
    # CRÉER UN NŒUD À PARTIR D'UN TEMPLATE
    # ============================================================

    def create_node(
        self,
        project_id,
        template_id,
        compute_id,
        name,
        x=0,
        y=0,
    ):

        url = (
            f"{self.base_url}/v2/projects/"
            f"{project_id}/templates/"
            f"{template_id}"
        )

        data = {
            "name": name,
            "compute_id": compute_id,
            "x": x,
            "y": y,
        }

        return self._request(
            "POST",
            url,
            json=data,
        )

    # ============================================================
    # CRÉER UN CLOUD
    # ============================================================

    def create_cloud_node(
        self,
        project_id,
        compute_id,
        name,
        x=0,
        y=0,
        interface_name=None,
    ):

        url = (
            f"{self.base_url}/v2/projects/"
            f"{project_id}/nodes"
        )

        data = {
            "name": name,
            "node_type": "cloud",
            "compute_id": compute_id,
            "x": x,
            "y": y,
        }

        if interface_name:

            data["properties"] = {
                "ports_mapping": [
                    {
                        "interface": interface_name,
                        "type": "ethernet",
                        "port_number": 0,
                        "name": interface_name,
                    }
                ]
            }

        return self._request(
            "POST",
            url,
            json=data,
        )

    # ============================================================
    # CRÉER UN LIEN
    # ============================================================

    def create_link(
        self,
        project_id,
        node_source_id,
        adapter_source,
        port_source,
        node_destination_id,
        adapter_destination,
        port_destination,
    ):

        url = (
            f"{self.base_url}/v2/projects/"
            f"{project_id}/links"
        )

        data = {
            "nodes": [
                {
                    "node_id": node_source_id,
                    "adapter_number": adapter_source,
                    "port_number": port_source,
                },
                {
                    "node_id": node_destination_id,
                    "adapter_number": adapter_destination,
                    "port_number": port_destination,
                },
            ]
        }

        return self._request(
            "POST",
            url,
            json=data,
        )

    # ============================================================
    # DÉMARRER UN NŒUD
    # ============================================================

    def start_node(
        self,
        project_id,
        node_id,
    ):

        node = self.get_node(
            project_id,
            node_id,
        )

        if node.get("node_type") == "cloud":
            return node

        status = node.get("status")

        if status in (
            "started",
            "running",
        ):
            return node

        url = (
            f"{self.base_url}/v2/projects/"
            f"{project_id}/nodes/"
            f"{node_id}/start"
        )

        return self._request(
            "POST",
            url,
        )

    # ============================================================
    # ARRÊTER UN NŒUD
    # ============================================================

    def stop_node(
        self,
        project_id,
        node_id,
    ):

        node = self.get_node(
            project_id,
            node_id,
        )

        if node.get("node_type") == "cloud":
            return node

        status = node.get("status")

        if status in (
            "stopped",
            "halted",
        ):
            return node

        url = (
            f"{self.base_url}/v2/projects/"
            f"{project_id}/nodes/"
            f"{node_id}/stop"
        )

        return self._request(
            "POST",
            url,
        )

    # ============================================================
    # ATTENDRE LE DÉMARRAGE D'UN NŒUD
    # ============================================================

    def wait_for_node_started(
        self,
        project_id,
        node_id,
        timeout=120,
        interval=3,
    ):

        start_time = time.time()

        last_status = None

        while time.time() - start_time < timeout:

            node = self.get_node(
                project_id,
                node_id,
            )

            last_status = node.get(
                "status"
            )

            print(
                f"[GNS3] "
                f"{node.get('name', node_id)} "
                f"status={last_status}"
            )

            if last_status in (
                "started",
                "running",
            ):
                return node

            time.sleep(
                interval
            )

        raise TimeoutError(
            f"Le nœud {node_id} "
            f"n'est pas démarré après "
            f"{timeout} secondes. "
            f"Dernier statut : "
            f"{last_status}"
        )

    # ============================================================
    # CONSOLE D'UN NŒUD
    # ============================================================

    def get_node_console(
        self,
        project_id,
        node_id,
    ):

        node = self.get_node(
            project_id,
            node_id,
        )

        return {
            "host": node.get(
                "console_host"
            ),
            "port": node.get(
                "console"
            ),
            "type": node.get(
                "console_type"
            ),
        }

    # ============================================================
    # ATTENDRE QUE LA CONSOLE SOIT DISPONIBLE
    # ============================================================

    def wait_for_console(
        self,
        project_id,
        node_id,
        timeout=120,
        interval=3,
    ):

        start_time = time.time()

        while time.time() - start_time < timeout:

            console = self.get_node_console(
                project_id,
                node_id,
            )

            if (
                console.get("host")
                and console.get("port")
            ):
                return console

            time.sleep(
                interval
            )

        raise TimeoutError(
            f"Console GNS3 indisponible "
            f"pour le nœud {node_id} "
            f"après {timeout} secondes."
        )