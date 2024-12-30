# %%
# Imports #

import os
import sys

import pandas as pd
import requests
from dotenv import load_dotenv

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_utils import data_dir, grandparent_dir, temp_upload_dir  # noqa: F401
from utils.display_tools import pprint_df, pprint_dict, print_logger  # noqa: F401

# %%
# Variables #

# source .env file
dotenv_path = os.path.join(grandparent_dir, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

BASE_URL = os.getenv("db_url")

# credentials
USERNAME = os.getenv("ht_auth_username", "")
PASSWORD = os.getenv("ht_auth_password", "")

if USERNAME == "" or PASSWORD == "":
    print("Please set the username and password in the .env file")
    raise ValueError("Please set the username and password in the .env file")


# %%
# Functinos #


def query_api(table_name):
    url = f"{BASE_URL}/query/"
    query = {"query": f"SELECT * FROM {table_name}"}
    # Make a GET request with authentication
    response = requests.get(url, params=query, auth=(USERNAME, PASSWORD))

    # Check the response
    if response.status_code != 200:
        print(
            f"Failed with status code: {response.status_code}, Message: {response.text}"
        )
        return None

    df = pd.DataFrame(response.json())
    return df


# %%
# Main #


if __name__ == "__main__":
    print("Querying API")
    table_name = "test_table"
    pprint_df(query_api(table_name))


# %%
