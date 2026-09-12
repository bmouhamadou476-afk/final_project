import requests


class GNS3Service:

    def __init__(
        self,
        host="127.0.0.1",
        port=3080,
        protocol="http",
        user=None,
        password=None,
        compute_id="local"
    ):

        self.base_url = (
            f"{protocol}://{host}:{port}"
        )

        self.compute_id = compute_id

        self.session = requests.Session()

        if user and password:

            self.session.auth = (
                user,
                password
            )


    # ==================================================
    # GESTION DES REQUETES HTTP
    # ==================================================

    def _request(
        self,
        method,
        url,
        **kwargs
    ):

        response = self.session.request(

            method=method,

            url=url,

            timeout=60,

            **kwargs

        )

        if not response.ok:

            try:

                error_data = (
                    response.json()
                )

            except Exception:

                error_data = (
                    response.text
                )

            raise ValueError(

                f"Erreur GNS3. "
                f"Status={response.status_code}, "
                f"URL={url}, "
                f"Reponse={error_data}"

            )

        if not response.content:

            return {}

        return response.json()


    # ==================================================
    # VERSION GNS3
    # ==================================================

    def get_version(self):

        url = (
            f"{self.base_url}"
            f"/v2/version"
        )

        return self._request(

            "GET",

            url

        )


    # ==================================================
    # COMPUTES
    # ==================================================

    def get_computes(self):

        url = (
            f"{self.base_url}"
            f"/v2/computes"
        )

        return self._request(

            "GET",

            url

        )


    def find_compute(
        self,
        compute_id
    ):

        computes = (
            self.get_computes()
        )

        for compute in computes:

            if (

                compute.get(
                    "compute_id"
                )

                ==

                compute_id

            ):

                return compute


        available_computes = [

            {

                "compute_id":
                    compute.get(
                        "compute_id"
                    ),

                "name":
                    compute.get(
                        "name"
                    ),

                "host":
                    compute.get(
                        "host"
                    ),

                "connected":
                    compute.get(
                        "connected"
                    )

            }

            for compute in computes

        ]


        raise ValueError(

            f"Compute GNS3 introuvable : "
            f"{compute_id}. "
            f"Computes disponibles : "
            f"{available_computes}"

        )


    # ==================================================
    # TEMPLATES
    # ==================================================

    def get_templates(self):

        url = (
            f"{self.base_url}"
            f"/v2/templates"
        )

        return self._request(

            "GET",

            url

        )


    def find_template(
        self,
        template_name
    ):

        templates = (
            self.get_templates()
        )

        template_name_lower = (

            template_name
            .lower()
            .strip()

        )


        for template in templates:

            current_name = (

                template
                .get(
                    "name",
                    ""
                )
                .lower()
                .strip()

            )


            if (

                current_name

                ==

                template_name_lower

            ):

                return template


        available_templates = [

            template.get(
                "name"
            )

            for template in templates

        ]


        raise ValueError(

            f"Template GNS3 introuvable : "
            f"{template_name}. "
            f"Templates disponibles : "
            f"{available_templates}"

        )


    # ==================================================
    # PROJETS
    # ==================================================

    def get_projects(self):

        url = (
            f"{self.base_url}"
            f"/v2/projects"
        )

        return self._request(

            "GET",

            url

        )


    def create_project(
        self,
        project_name
    ):

        url = (
            f"{self.base_url}"
            f"/v2/projects"
        )

        payload = {

            "name":
                project_name

        }


        return self._request(

            "POST",

            url,

            json=payload

        )


    def get_or_create_project(
        self,
        project_name
    ):

        projects = (
            self.get_projects()
        )


        for project in projects:

            if (

                project.get(
                    "name"
                )

                ==

                project_name

            ):

                return project


        return self.create_project(

            project_name

        )


    def open_project(
        self,
        project_id
    ):

        url = (
            f"{self.base_url}"
            f"/v2/projects/"
            f"{project_id}"
            f"/open"
        )

        return self._request(

            "POST",

            url

        )


    # ==================================================
    # NODES
    # ==================================================

    def get_nodes(
        self,
        project_id
    ):

        url = (
            f"{self.base_url}"
            f"/v2/projects/"
            f"{project_id}"
            f"/nodes"
        )

        return self._request(

            "GET",

            url

        )


    def get_node(
        self,
        project_id,
        node_id
    ):

        url = (
            f"{self.base_url}"
            f"/v2/projects/"
            f"{project_id}"
            f"/nodes/"
            f"{node_id}"
        )

        return self._request(

            "GET",

            url

        )


    def delete_node(
        self,
        project_id,
        node_id
    ):

        url = (
            f"{self.base_url}"
            f"/v2/projects/"
            f"{project_id}"
            f"/nodes/"
            f"{node_id}"
        )

        return self._request(

            "DELETE",

            url

        )


    # ==================================================
    # NETTOYAGE DU PROJET
    # ==================================================

    def clear_project(
        self,
        project_id
    ):

        nodes = (
            self.get_nodes(
                project_id
            )
        )


        for node in nodes:

            node_id = (
                node.get(
                    "node_id"
                )
            )


            if node_id:

                self.delete_node(

                    project_id,

                    node_id

                )


    # ==================================================
    # CREATION NODE DEPUIS TEMPLATE
    # ==================================================

    def create_node(
        self,
        project_id,
        name,
        x,
        y,
        template_id,
        compute_id=None
    ):

        if compute_id is None:

            compute_id = (
                self.compute_id
            )


        self.find_compute(
            compute_id
        )


        url = (
            f"{self.base_url}"
            f"/v2/projects/"
            f"{project_id}"
            f"/templates/"
            f"{template_id}"
        )


        payload = {

            "name":
                name,

            "x":
                x,

            "y":
                y,

            "compute_id":
                compute_id

        }


        return self._request(

            "POST",

            url,

            json=payload

        )


    # ==================================================
    # CREATION CLOUD
    # ==================================================

    def create_cloud_node(
        self,
        project_id,
        name,
        x,
        y,
        interface_name,
        compute_id=None
    ):

        if compute_id is None:

            compute_id = (
                self.compute_id
            )


        # Vérifie que le compute existe

        self.find_compute(
            compute_id
        )


        url = (
            f"{self.base_url}"
            f"/v2/projects/"
            f"{project_id}"
            f"/nodes"
        )


        # Interface Cloud
        #
        # "special" est obligatoire dans le schéma
        # utilisé par ton GNS3 VM.

        interface = {

            "name":
                interface_name,

            "type":
                "ethernet",

            "special":
                False

        }


        payload = {

            "name":
                name,

            "node_type":
                "cloud",

            "compute_id":
                compute_id,

            "x":
                x,

            "y":
                y,

            "properties": {

                "interfaces": [

                    interface

                ]

            }

        }


        return self._request(

            "POST",

            url,

            json=payload

        )


    # ==================================================
    # LIENS
    # ==================================================

    def create_link(
        self,
        project_id,
        node_source_id,
        adapter_source,
        port_source,
        node_destination_id,
        adapter_destination,
        port_destination
    ):

        url = (
            f"{self.base_url}"
            f"/v2/projects/"
            f"{project_id}"
            f"/links"
        )


        payload = {

            "nodes": [

                {

                    "node_id":
                        node_source_id,

                    "adapter_number":
                        adapter_source,

                    "port_number":
                        port_source

                },

                {

                    "node_id":
                        node_destination_id,

                    "adapter_number":
                        adapter_destination,

                    "port_number":
                        port_destination

                }

            ]

        }


        return self._request(

            "POST",

            url,

            json=payload

        )


    # ==================================================
    # DEMARRAGE
    # ==================================================

    def start_node(
        self,
        project_id,
        node_id
    ):

        url = (
            f"{self.base_url}"
            f"/v2/projects/"
            f"{project_id}"
            f"/nodes/"
            f"{node_id}"
            f"/start"
        )


        return self._request(

            "POST",

            url

        )


    # ==================================================
    # ARRET
    # ==================================================

    def stop_node(
        self,
        project_id,
        node_id
    ):

        url = (
            f"{self.base_url}"
            f"/v2/projects/"
            f"{project_id}"
            f"/nodes/"
            f"{node_id}"
            f"/stop"
        )


        return self._request(

            "POST",

            url

        )
        # ==================================================
    # RECUPERATION DES INFORMATIONS DE CONSOLE
    # ==================================================

    def get_node_console(
        self,
        project_id,
        node_id,
    ):

        node = (

            self.get_node(
                project_id,
                node_id,
            )

        )


        console_host = (

            node.get(
                "console_host"
            )

        )


        console_port = (

            node.get(
                "console"
            )

        )


        console_type = (

            node.get(
                "console_type"
            )

        )


        if not console_host:

            raise ValueError(

                f"console_host introuvable "
                f"pour le node {node_id}"

            )


        if console_port is None:

            raise ValueError(

                f"console introuvable "
                f"pour le node {node_id}"

            )


        return {

            "host":
                console_host,

            "port":
                console_port,

            "type":
                console_type

        }