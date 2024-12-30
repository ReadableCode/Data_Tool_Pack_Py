# %%

import os
import sys

import requests
from dotenv import load_dotenv

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_utils import data_dir, grandparent_dir, temp_upload_dir
from utils.display_tools import pprint_dict, print_logger

# %%
# source .env file
dotenv_path = os.path.join(grandparent_dir, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

base_url = os.getenv("db_url")
# URL of the DuckDB service
url = f"{base_url}/query/"
print(url)

# credentials
username = os.getenv("ht_auth_username")
password = os.getenv("ht_auth_password")


# %%

query = {"query": "SELECT * FROM test_table"}
# Make a GET request with authentication
response = requests.get(url, params=query, auth=(username, password))

# Check the response
if response.status_code == 200:
    print("Success:", response.json())  # Assuming the response is JSON
    print(response.json())  # Assuming the response is JSON
else:
    print(f"Failed with status code: {response.status_code}, Message: {response.text}")


# %%
