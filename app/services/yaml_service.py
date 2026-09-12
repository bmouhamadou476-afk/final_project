from pathlib import Path

import yaml

from app.schemas.topology_yaml import (
    TopologyYAML
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)


def load_topology_yaml():

    yaml_path = (
        BASE_DIR
        / "topology.yml"
    )


    if not yaml_path.exists():

        raise FileNotFoundError(

            f"Fichier YAML introuvable : "
            f"{yaml_path}"

        )


    with open(

        yaml_path,

        "r",

        encoding="utf-8"

    ) as file:

        data = yaml.safe_load(
            file
        )


    if data is None:

        raise ValueError(
            "Le fichier topology.yml est vide"
        )


    return TopologyYAML(
        **data
    )