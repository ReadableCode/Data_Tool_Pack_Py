# %%
# Imports #

import os

import pandas as pd  # noqa: F401
from config import grandparent_dir
from jira import JIRA
from dotenv import load_dotenv
from utils.display_tools import (  # noqa: F401
    pprint_df,
    pprint_dict,
    pprint_ls,
    print_logger,
)

# %%
# Variables #

# source .env file
dotenv_path = os.path.join(grandparent_dir, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_USER = os.getenv("JIRA_USER")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_PROJECT = os.getenv("JIRA_PROJECT")
assert (
    JIRA_SERVER is not None
    and JIRA_USER is not None
    and JIRA_TOKEN is not None
    and JIRA_PROJECT is not None
), "Missing one or more: JIRA_SERVER, JIRA_USER, JIRA_TOKEN"


# Establish a connection using basic authentication
jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USER, JIRA_TOKEN))


# %%
# Functions #


def pprint_dict_with_paths(d, prefix=""):
    """
    Recursively prints all key-value pairs in a dictionary, displaying the full path (address) of each value.

    :param d: Dictionary to print
    :param prefix: Used for recursion to track the key path
    """
    if isinstance(d, dict):
        for k, v in d.items():
            new_prefix = f"{prefix}.{k}" if prefix else k  # Construct the full address
            pprint_dict_with_paths(v, new_prefix)
    elif isinstance(d, list):
        for i, v in enumerate(d):
            new_prefix = f"{prefix}[{i}]"  # Address for list elements
            pprint_dict_with_paths(v, new_prefix)
    else:
        print(f"{prefix}: {d}")  # Fix: use 'd' directly, not 'v'


def print_issue(issue_dict, indent=0):
    # print each key value if vvalue is not None or "None
    for k, v in issue_dict.items():
        if v is not None and v != "None" and v != "Null" and v != "":
            if isinstance(v, dict):
                print_issue(v, indent + 2)
            elif isinstance(v, list):
                for i in v:
                    if isinstance(i, dict):
                        print_issue(i, indent + 2)
                    else:
                        if i is not None and i != "None" and i != "Null" and i != "":
                            print(f"{indent*' '}{k}: {i}")
            elif isinstance(v, str):
                if v is not None and v != "None" and v != "Null" and v != "":
                    print(f"{indent*' '}{k}: {v}")


def get_issues(project: str, max_results: int = 20):
    """
    Fetches issues from the specified JIRA project.

    :param project: JIRA project key
    :param max_results: Number of issues to retrieve
    :return: List of issue objects
    """
    response = jira.search_issues(
        f"project = {project}", maxResults=max_results, json_result=True
    )

    issues = response.get("issues", [])  # Extract actual issues list
    issues_struct = {}

    if issues:
        for issue in issues:
            # pprint_dict_with_paths(issue)
            issue_title = issue["fields"]["summary"]
            issue_key = issue["key"]

            print(f"Found issue {issue_key}: {issue_title}")
            issues_struct[issue_key] = {}
            issues_struct[issue_key]["title"] = issue_title
    else:
        print(f"No issues found in project {project}")

    return issues_struct


def add_issue(summary: str, description: str, issue_type: str = "Task"):
    """
    Creates a new issue in JIRA under the configured project and moves it to 'In Progress'.

    :param summary: Summary of the issue
    :param description: Detailed description of the issue
    :param issue_type: Type of issue (default: Task)
    :return: Created issue object
    """
    new_issue = jira.create_issue(
        fields={
            "project": {"key": JIRA_PROJECT},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }
    )

    print(f"Issue {new_issue.key} created successfully!")

    # Move the issue to "In Progress" if possible
    transitions = jira.transitions(new_issue)
    transition_id = None
    for t in transitions:
        if t["name"].lower() == "in progress":
            transition_id = t["id"]
            break

    if transition_id:
        jira.transition_issue(new_issue, transition_id)
        print(f"Issue {new_issue.key} moved to 'In Progress'")
    else:
        print(
            f"Could not move {new_issue.key} to 'In Progress' (Transition ID not found)"
        )

    return new_issue


# %%
# Main #


issues_struct = get_issues(JIRA_PROJECT, max_results=2)
pprint_dict(issues_struct)


# %%
