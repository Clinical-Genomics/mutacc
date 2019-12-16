from copy import deepcopy
import tempfile
from pathlib import Path
import subprocess
import os

import click
import yaml

CONTAINER_ROOT_DIR = "/mutacc-data/"


def create_volume_string(file_path_host):
    """
        Create volume based on file path on host
    """

    file_path_container = container_file_path(
        container_root_dir=CONTAINER_ROOT_DIR, file_path_host=file_path_host
    )
    return ":".join([file_path_host, file_path_container, "ro"])


def container_file_path(container_root_dir, file_path_host):

    """
        Set file path in container
    """

    container_root_dir_path = Path(container_root_dir)
    file_name = Path(file_path_host).name
    return str(container_root_dir_path / file_name)


def parse_yaml(yaml_file):

    """
        Parse yaml file into dict
    """
    with open(yaml_file) as file_handle:
        parsed_file = yaml.load(file_handle)
    return parsed_file


def change_paths(host_case):

    """
        Change file paths in dict to corresponding paths in container
    """
    volumes = []
    cont_case = deepcopy(host_case)
    cont_case["variants"] = container_file_path(
        CONTAINER_ROOT_DIR, host_case["variants"]
    )
    volumes.append(create_volume_string(host_case["variants"]))

    for sample in cont_case["samples"]:
        volumes.append(create_volume_string(sample["bam_file"]))
        volumes.append(create_volume_string(sample["bam_file"] + ".bai"))
        sample["bam_file"] = container_file_path(CONTAINER_ROOT_DIR, sample["bam_file"])

    return cont_case, volumes


def write_yaml(data_dict):

    """
        Write yaml file
    """

    with tempfile.NamedTemporaryFile(mode="wt", delete=False, dir=".") as file_handle:
        yaml.dump(data_dict, file_handle)
        file_name = file_handle.name
    return file_name


# Create CLI entrypoint with click
@click.command()
@click.option("--case-file", "-c", type=click.Path(exists=True))
@click.option("--padding", "-p", type=int)
def docker_wrapper(case_file, padding):

    case_data = parse_yaml(case_file)
    case_data, volumes = change_paths(case_data)
    tmp_case_name = write_yaml(case_data)
    volumes.append(create_volume_string(tmp_case_name))
    arguments = ["docker-compose", "run"]
    for volume in volumes:
        arguments.extend(["-v", volume])
    arguments.append("--rm")
    arguments.extend(
        [
            "mutacc",
            "extract",
            "--case",
            container_file_path(CONTAINER_ROOT_DIR, tmp_case_name),
        ]
    )
    if padding:
        arguments.extend(["--padding", padding])
    subprocess.run(arguments)
    os.remove(tmp_case_name)


if __name__ == "__main__":

    # Run CLI entrypoint
    docker_wrapper()
