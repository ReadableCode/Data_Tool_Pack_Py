# %%
# Imports #

import datetime
import json
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
# Functions #


def authenticated_request(method, endpoint, **kwargs):
    url = f"{BASE_URL}{endpoint}"
    response = requests.request(method, url, auth=(USERNAME, PASSWORD), **kwargs)

    if response.status_code != 200:
        print(
            f"Failed with status code: {response.status_code}, Message: {response.text}"
        )
        return None
    return response.json()


def create_table(table_name, columns):
    """
    Create a table dynamically.
    """
    data = {"table_name": table_name, "columns": columns}
    return authenticated_request("POST", "/create_table/", json=data)


def insert_data(table_name, data):
    """
    Insert data into a specified table.
    """
    payload = {"table_name": table_name, "data": data}
    return authenticated_request("POST", "/insert/", json=payload)


def query_data(query, table_name=None):
    """
    Query data from the database.
    """
    params = {"query": query, "table_name": table_name}
    json_data = authenticated_request("GET", "/query/", params=params)

    if json_data is None:
        return pd.DataFrame()

    df = pd.DataFrame(json_data)

    return df


def upload_data(table_name, file_path):
    """
    Upload CSV or Parquet data to a specified table.
    """
    with open(file_path, "rb") as file:
        files = {"file": file}
        params = {"table_name": table_name}
        return authenticated_request("POST", "/upload/", params=params, files=files)


def health_check():
    """
    Perform a health check of the API.
    """
    return authenticated_request("GET", "/")


def list_tables():
    """
    List all tables in the DuckDB database.
    """
    query = (
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main';"
    )
    response = query_data(query=query)
    return response


def ensure_heartbeat_table():
    """
    Ensure the heartbeat table exists with columns for datetime and notes.
    """
    table_name = "heartbeat"
    columns = "timestamp DATETIME, notes TEXT"
    params = {"table_name": table_name, "columns": columns}

    # Call the API with query parameters
    response = authenticated_request("POST", "/create_table/", params=params)

    if response:
        print(f"Heartbeat table ensured: {response}")
    else:
        print(f"Failed to ensure heartbeat table.")


def add_heartbeat(note=""):
    """
    Add a heartbeat entry with the current timestamp and a note.
    """
    table_name = "heartbeat"
    timestamp = datetime.datetime.now().isoformat()  # Current timestamp
    data = {"timestamp": timestamp, "notes": note}
    response = insert_data(table_name, data)
    if response:
        print(f"Heartbeat added: {response}")


def get_heartbeat_table():
    """
    Return the contents of the heartbeat table.
    """
    return query_data(query="SELECT * FROM heartbeat", table_name="heartbeat")


# %%
# Main #


if __name__ == "__main__":
    print("Querying API")

    # Health Check
    print("Health Check")
    pprint_dict(health_check())

    # List Tables
    print("List Tables")
    tables = list_tables()
    pprint_dict(tables)

    # Query Data
    table_name = "test_table"
    pprint_df(query_data(query=f"SELECT * FROM {table_name}", table_name=table_name))

    print("Managing Heartbeat Table")

    # Ensure the heartbeat table exists
    ensure_heartbeat_table()

    # Add a new heartbeat with a note
    add_heartbeat(note="heartbeat note")

    # Retrieve and display the heartbeat table
    print("Heartbeat Table:")
    heartbeat_df = get_heartbeat_table()
    pprint_df(heartbeat_df)


# %%
