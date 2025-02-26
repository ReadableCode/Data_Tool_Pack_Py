# %%
# Imports #

import os

import pandas as pd  # noqa: F401
from config import grandparent_dir
from jira import JIRA
from dotenv import load_dotenv
from utils.display_tools import pprint_df, pprint_ls, print_logger  # noqa: F401

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

# Example: search for issues in a specific project (adjust JQL as needed)
issues = jira.search_issues(f"project = FINOPSCR", maxResults=5)

print("Found issues:")
for issue in issues:
    print(f"{issue.key}: {issue.fields.summary}")

# %%
