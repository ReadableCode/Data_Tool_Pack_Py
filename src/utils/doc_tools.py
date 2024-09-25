# %%
# Imports #

import os
import sys

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_utils import grandparent_dir

# %%
# Variables #

docs_dir = os.path.join(grandparent_dir, "docs")


# %%
# Link Formatting Tools #


def get_git_link(script_path, repo_owner, repo_name, branch_name):
    """
    Gets the link to the Git repository.

    Returns:
        str: The link to the Git repository.
    """

    return (
        f"https://github.com/{repo_owner}/{repo_name}/blob/{branch_name}/{script_path}"
    )


def get_git_link_formula(script_path, repo_owner, repo_name, branch_name):
    git_link = get_git_link(
        script_path, repo_owner=repo_owner, repo_name=repo_name, branch_name=branch_name
    )
    return f'=hyperlink("{git_link}","Link")'


def get_sheet_link(sheet_id):
    if (sheet_id == "") or (sheet_id is None) or (len(sheet_id) != 44):
        return ""
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}"


def get_sheet_link_formula(sheet_id):
    sheet_link = get_sheet_link(sheet_id)
    if sheet_link == "":
        return ""
    return f'=hyperlink("{sheet_link}","Link")'


def get_google_drive_folder_link(folder_id):
    if (folder_id == "") or (folder_id is None) or (len(folder_id) != 33):
        return ""
    return f"https://drive.google.com/drive/folders/{folder_id}"


def get_domo_link(domo_table_id):
    if (domo_table_id == "") or (domo_table_id is None):
        return ""
    return f"https://hellofresh.domo.com/datasources/{domo_table_id}/details/data/table"


def convert_to_domo_link(domo_table_id):
    domo_link = get_domo_link(domo_table_id)
    if domo_link == "":
        return ""
    return f'=hyperlink("{domo_link}","Link")'


def get_link_from_resource_type(
    resource_type,
    resource_path="",
    resource_id="",
):
    if resource_type == "google_sheet":
        link = get_sheet_link(resource_id)
    elif resource_type == "google_drive_folder":
        link = get_google_drive_folder_link(resource_id)
    elif resource_type == "domo_table":
        link = get_domo_link(resource_id)
    elif resource_type == "git":
        link = get_git_link(resource_path)
    else:
        link = ""

    if link == "":
        return ""

    return link


# %%
# Markdown Tools #

dict_markdown_levels = {
    1: {
        "newlines_before": "\n",
        "header": "# ",
        "newlines_after": "\n",
    },
    2: {
        "newlines_before": "\n",
        "header": "## ",
        "newlines_after": "\n",
    },
    3: {
        "newlines_before": "\n",
        "header": "- ### ",
        "newlines_after": "\n",
    },
    4: {
        "newlines_before": "\n",
        "header": "  - ",
        "newlines_after": "\n",
    },
    5: {
        "newlines_before": "\n",
        "header": "    - ",
        "newlines_after": "\n",
    },
}


def get_markdown_line(level, name, link=""):
    if link != "":
        name = f"[{name}]"
        link = f"({link})"

    newlines_before = dict_markdown_levels[level]["newlines_before"]
    header = dict_markdown_levels[level]["header"]
    newlines_after = dict_markdown_levels[level]["newlines_after"]

    return f"{newlines_before}{header}{name}{link}{newlines_after}"


# %%
