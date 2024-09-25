# %%
# Imports #

import os
import shutil

from utils.display_tools import print_logger

# %%
# Functions #


def copy_non_existant_files_from_backup_with_datestamp(
    file_path_backup_dir, file_path_recovery, dry_run=True
):
    print_logger("#" * 80)
    print_logger(f"file_path_backup_dir: {file_path_backup_dir}")
    print_logger(f"file_path_recovery: {file_path_recovery}")
    print_logger("#" * 80)

    # create folder for restore if it doesn't exist
    if not os.path.exists(file_path_recovery):
        print(f"Creating folder: {file_path_recovery}")
        if not dry_run:
            os.makedirs(file_path_recovery)
        else:
            print(f"Would create folder: {file_path_recovery}")

    # Get the full paths of the first 10 files in each directory
    ls_file_paths_in_backup_dir = [
        os.path.join(file_path_backup_dir, file)
        for file in os.listdir(file_path_backup_dir)
    ]
    ls_file_paths_in_recovery_dir = [
        os.path.join(file_path_recovery, file)
        for file in os.listdir(file_path_recovery)
    ]

    for file_path_of_backup_file in ls_file_paths_in_backup_dir:
        print_logger(f"Checking file_path_of_backup_file: {file_path_of_backup_file}")
        if os.path.isdir(file_path_of_backup_file):
            print("Using recursion to copy files in subdirectories")
            copy_non_existant_files_from_backup_with_datestamp(
                file_path_of_backup_file,
                os.path.join(
                    file_path_recovery, os.path.basename(file_path_of_backup_file)
                ),
                dry_run=dry_run,
            )
            continue
        file_name_backup_file_without_stamp_no_ext = file_path_of_backup_file.split(
            "~"
        )[0]
        file_stamp_backup_file = file_path_of_backup_file.split("~")[1].split(".")[0]
        file_name_extensions_backup_file = file_path_of_backup_file.split("~")[1].split(
            "."
        )[1]
        file_name_backup_file_without_stamp = (
            file_name_backup_file_without_stamp_no_ext
            + "."
            + file_name_extensions_backup_file
        )
        print(
            f"file_name_backup_file_without_stamp: {file_name_backup_file_without_stamp}"
        )
        print(f"file_stamp_backup_file: {file_stamp_backup_file}")

        # See if file without stamp exists in recovery directory
        found_file_in_recovery = False
        for possible_file_path_in_recovery_dir in ls_file_paths_in_recovery_dir:
            if (
                file_name_backup_file_without_stamp
                in possible_file_path_in_recovery_dir
            ):
                print(
                    f"Found file in recovery directory: {file_name_backup_file_without_stamp}"
                )
                found_file_in_recovery = True
                break

        if not found_file_in_recovery:
            print(
                f"File not found in recovery directory: {file_name_backup_file_without_stamp}"
            )
            # copy file to recovery directory
            dest_copy_path = os.path.join(
                file_path_recovery, os.path.basename(file_path_of_backup_file)
            )
            if not dry_run:
                print(f"Copying from {file_path_of_backup_file} to {dest_copy_path}")
                shutil.copy2(file_path_of_backup_file, dest_copy_path)
            else:
                print(f"Would copy from {file_path_of_backup_file} to {dest_copy_path}")


def clean_datestamped_versions_if_non_datestamped_exists(
    file_path_recovery, dry_run=True
):
    print_logger("#" * 80)
    print_logger(f"starting to clean directory: {file_path_recovery}")
    print_logger("#" * 80)

    ls_file_paths_in_recovery_dir = [
        os.path.join(file_path_recovery, file)
        for file in os.listdir(file_path_recovery)
    ]

    for file_path_in_recovery_dir in ls_file_paths_in_recovery_dir:
        if os.path.isdir(file_path_in_recovery_dir):
            print(
                f"Using recursion to clean files in subdirectory: {file_path_in_recovery_dir}"
            )
            clean_datestamped_versions_if_non_datestamped_exists(
                file_path_in_recovery_dir,
                dry_run=dry_run,
            )
            continue
        file_name_in_recovery_dir = os.path.basename(file_path_in_recovery_dir)

        if "~" not in file_name_in_recovery_dir:
            continue

        file_name_without_stamp_no_ext = file_name_in_recovery_dir.split("~")[0]
        file_name_extensions = file_name_in_recovery_dir.split("~")[1].split(".")[1]
        file_name_without_stamp = (
            file_name_without_stamp_no_ext + "." + file_name_extensions
        )
        file_path_without_stamp = os.path.join(
            file_path_recovery, file_name_without_stamp
        )
        print(
            f"Checking if should keep file_name_in_recovery_dir: {file_name_in_recovery_dir}"
        )

        # See if file without stamp exists in recovery directory

        if os.path.exists(file_path_without_stamp):
            print(f"Found file in recovery directory: {file_path_without_stamp}")
            if not dry_run:
                print(f"-------- Deleting file: {file_path_in_recovery_dir}")
                os.remove(file_path_in_recovery_dir)
            else:
                print(f"Would delete file: {file_path_in_recovery_dir}")
        else:
            print(f"File not found in recovery directory: {file_name_without_stamp}")
            # rename file to file without stamp
            if not dry_run:
                print(
                    f"---------- Renaming from {file_path_in_recovery_dir} to {file_path_without_stamp}"
                )
                os.rename(file_path_in_recovery_dir, file_path_without_stamp)
            else:
                print(
                    f"Would rename from {file_path_in_recovery_dir} to {file_path_without_stamp}"
                )

        print("")


# %%
# Main #

# Set dry_run to False to actually copy files
dry_run = True

file_path_backup_dir = "F:\\HelloFresh\\ProjectsSTVersions\\HF_Finance\\reports"
file_path_recovery = "F:\\HelloFresh\\GDrive\\Google_Items\\reports"

# copy_non_existant_files_from_backup_with_datestamp(
#     file_path_backup_dir, file_path_recovery, dry_run=dry_run
# )
# clean_datestamped_versions_if_non_datestamped_exists(
#     file_path_recovery, dry_run=dry_run
# )


# %%
