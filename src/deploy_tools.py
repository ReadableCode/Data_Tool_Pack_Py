# %%
# Imports #

import difflib
import json
import os
import shutil
import time

from config import data_dir
from utils.config_utils import great_grandparent_dir
from utils.display_tools import pprint_dict, print_logger  # noqa: F401

# %%
# Variables #

with open(os.path.join(data_dir, "dict_file_deployments_detailed.json"), "r") as f:
    dict_file_deployments_detailed = json.load(f)


# %%
# Functions #


def deploy_file_with_diff_and_conf(src_file, dest_file, dry_run=True):
    """
    Synchronizes a file from the source location to the destination location, with optional confirmation
    and backup steps if differences are detected. If `dry_run` is enabled, no changes are made, but actions
    are logged.

    The function performs the following actions:
    1. Checks if the destination directory exists; if not, it skips further processing.
    2. If the destination file doesn't exist, it either logs the action (in dry-run mode) or copies the source file to the destination.
    3. If the destination file exists, compares the content with the source file and logs the differences.
    4. In `dry_run` mode, it stops after displaying the differences. Otherwise, it prompts the user to choose whether to trust the source or destination file:
       - If the source is chosen, the function backs up the destination file before overwriting it.
       - If the destination is chosen, the function copies it back to the source location.

    Args:
        src_file (str): The absolute path to the source file to be copied.
        dest_file (str): The absolute path to the destination file to be synchronized.
        dry_run (bool, optional): If True, the function only logs actions without making any changes. Defaults to True.

    Raises:
        FileNotFoundError: If the source file does not exist.

    Note:
        - This function relies on `print_logger()` for logging and `shutil` for file operations.
        - It creates a timestamped backup of the destination file in an 'archive' folder if the source file is chosen to overwrite.

    Example:
        synchronize_file_with_confirmation("/path/to/source/file.txt", "/path/to/dest/file.txt", dry_run=False)
    """
    if not os.path.exists(os.path.dirname(dest_file)):
        # create it
        print_logger(
            f"{' '*4}Destination directory {os.path.dirname(dest_file)} does not exist."
        )
        if dry_run:
            print_logger(
                f"{' '*4}Would create directory {os.path.dirname(dest_file)} and copy {src_file} to {dest_file}"
            )
            return
        else:
            print_logger(
                f"{' '*4}Creating directory {os.path.dirname(dest_file)} and copying {src_file} to {dest_file}"
            )
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.copy(src_file, dest_file)

    if not os.path.exists(dest_file):
        print_logger(f"{' '*4}Destination file {dest_file} does not exist.")
        if dry_run:
            print_logger(
                f"{' '*4}Would copy {src_file} to {dest_file} for the first time"
            )
            return
        else:
            print_logger(f"{' '*4}Copying {src_file} to {dest_file} for the first time")
            shutil.copy(src_file, dest_file)
            return

    # if file path is not in ls_diff_and_backup_file_types, skip diffing and just copy
    ls_diff_and_backup_file_types = [".env", ".dev"]
    if all(
        not dest_file.endswith(file_type) for file_type in ls_diff_and_backup_file_types
    ):
        print_logger(
            f"{' '*4}Skipping diffing for {dest_file} as it is not in ls file types to diff"
        )
        if dry_run:
            print_logger(
                f"{' '*4}Would copy {src_file} to {dest_file} without diffing/checking if diff"
            )
            return
        else:
            print_logger(
                f"{' '*4}Copying {src_file} to {dest_file} without diffing/checking if diff"
            )
            shutil.copy(src_file, dest_file)
            return

    # Compare existing files
    with open(src_file, "r") as src, open(dest_file, "r") as dest:
        src_lines = src.readlines()
        dest_lines = dest.readlines()
        diff = list(
            difflib.context_diff(
                dest_lines, src_lines, fromfile=dest_file, tofile=src_file
            )
        )

    if not diff:
        print_logger(
            f"{' '*4}No differences found between {src_file} and {dest_file}. Skipping copy."
        )
        return

    print_logger(f"{' '*4}Differences found between {src_file} and {dest_file}:")
    for line in diff:
        print_logger(f"{' '*8}" + line.strip())

    if dry_run:
        print_logger(
            f"{' '*8}Would ask to copy or ingest src:{src_file}, dest:{dest_file} like this:"
        )
        print_logger(
            f"{' '*8}Would you like to trust the file at:\n{' '*38}{dest_file} (d)\n{' '*38}or the file at\n{' '*38}{src_file} (s)?"
        )
    else:
        # Use a simple text prompt to ask the user
        while True:
            trusted_file = (
                input(
                    f"{' '*8}Would you like to trust the file at:\n{dest_file} (d)\nor the file at\n{src_file} (s)?"
                )
                .strip()
                .lower()
            )

            if trusted_file in ["d", "s"]:
                break
            else:
                print_logger(
                    f"{' '*4}Invalid input. Please enter 'd' for destination or 's' for source."
                )

        if trusted_file == "s":
            print_logger(
                f"{' '*4}Copying {dest_file} to backup in {os.path.dirname(src_file)}"
            )
            backup_path = os.path.join(
                os.path.dirname(src_file),
                "archive",
                # rel path in the dest project
                f"{os.path.join(*os.path.relpath(os.path.dirname(dest_file), great_grandparent_dir).split(os.sep))}",
                f"{os.path.basename(dest_file)}_{time.strftime('%Y%m%d%H%M%S')}",
            )
            # make sure backup path directories exist
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy(dest_file, backup_path)
            print_logger(f"{' '*4}Copying {src_file} to {dest_file}")
            shutil.copy(src_file, dest_file)
        elif trusted_file == "d":
            print_logger(f"{' '*4}Copying {dest_file} to {src_file}")
            shutil.copy(dest_file, src_file)


# %%
# Main #

if __name__ == "__main__":
    ls_work_projects = [
        "na-finops",
        "na-fin-data-streamlit",
        "na-faba",
        "snowflake-db-finops-debit",
    ]
    if os.path.exists(os.path.join(great_grandparent_dir, "Our_Cash")):
        ls_project_types_to_run = ["personal"]
    else:
        ls_project_types_to_run = ["work"]

    dry_run = False
    for (
        src_file_deployment_name,
        src_file_deployment_config,
    ) in dict_file_deployments_detailed.items():
        print_logger(f"Deploying {src_file_deployment_name}...", as_break=True)
        ls_src_path = src_file_deployment_config["ls_src_path"]
        src_path = os.path.join(great_grandparent_dir, *ls_src_path)
        src_project = ls_src_path[0]
        src_project_type = "work" if src_project in ls_work_projects else "personal"
        ls_dest_path_lists = src_file_deployment_config["ls_deployment_dests"]
        for dest_path_list in ls_dest_path_lists:
            dest_project = dest_path_list[0]
            dest_project_type = (
                "work" if dest_project in ls_work_projects else "personal"
            )
            dest_path = os.path.join(great_grandparent_dir, *dest_path_list)
            if dest_project_type not in ls_project_types_to_run:
                print_logger(
                    f"Skipping deployment to {dest_path} as it is not in ls_project_types_to_run"
                )
                continue
            print_logger(
                f"Running deploy_file_with_diff_and_conf src_file:{src_path} to dest_file:{dest_path}"
            )
            deploy_file_with_diff_and_conf(src_path, dest_path, dry_run=dry_run)

    print_logger("Done", as_break=True)


# %%
