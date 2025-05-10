# %%
# Imports #

import json
import os
import sys

import requests
from dotenv import load_dotenv

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_utils import data_dir, grandparent_dir  # noqa F401
from utils.display_tools import (  # noqa F401
    pprint_df,
    pprint_dict,
    pprint_ls,
    print_logger,
)
from utils.pandas_tools import (  # noqa F401
    generate_schema_from_df,
    print_schema_yaml_limesync_format,
)

# %%
# Load Environment #

# source .env file
dotenv_path = os.path.join(grandparent_dir, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


BASE_URL = os.getenv("SALAD_AND_GO_BASE_URL")
USERNAME = os.getenv("TRACI_SALAD_AND_GO_USERNAME")
PASSWORD = os.getenv("TRACI_SALAD_AND_GO_PASSWORD")

LS_COMMUNITIES = ["Salad and Go"]


def get_oauth_access_token():
    url = f"{BASE_URL}/oauth_accesstoken"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {"grant_type": "password", "email": USERNAME, "password": PASSWORD}

    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)

    print("Status:", response.status_code)
    print("Text:", repr(response.text))
    print("Headers:", response.headers)

    if "application/json" not in response.headers.get("Content-Type", ""):
        raise Exception("Response is not JSON")

    return response.json()["access_token"]


print(get_oauth_access_token())


# %%
