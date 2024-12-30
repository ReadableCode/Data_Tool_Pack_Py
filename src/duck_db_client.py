# %%

import os

import requests
from config import grandparent_dir
from dotenv import load_dotenv

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
