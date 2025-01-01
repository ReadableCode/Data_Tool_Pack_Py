# %%
# Imports #

import datetime
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


def health_check():
    """
    Perform a health check of the API.
    """
    url = f"{BASE_URL}/"
    response = requests.get(url, auth=(USERNAME, PASSWORD))

    if response.status_code != 200:
        print(
            f"Failed with status code: {response.status_code}, Message: {response.text}"
        )
        return None
    return response.json()


def raw_query(query, params=None):
    """
    Execute a raw SQL query.
    """
    url = f"{BASE_URL}/raw_query/"
    payload = {"query": query, "params": params or []}
    response = requests.post(url, json=payload, auth=(USERNAME, PASSWORD))

    if response.status_code != 200:
        print(
            f"Failed with status code: {response.status_code}, Message: {response.text}"
        )
        return None
    return response.json()


def list_tables():
    """
    List all tables in the DuckDB database.
    """
    query = (
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main';"
    )
    json_data = raw_query(query=query)

    if not json_data or not json_data.get("data"):
        return None

    df_tables = pd.DataFrame(json_data["data"])
    return df_tables


def ensure_heartbeat_table():
    """
    Ensure the heartbeat table exists with columns for datetime and notes.
    """
    query = "CREATE TABLE IF NOT EXISTS heartbeat (timestamp DATETIME, notes TEXT);"
    response = raw_query(query=query)

    if response:
        print("Heartbeat table ensured.")
    else:
        print("Failed to ensure heartbeat table.")


def add_heartbeat(note=""):
    """
    Add a heartbeat entry with the current timestamp and a note.
    """
    timestamp = datetime.datetime.now().isoformat()  # Current timestamp
    query = "INSERT INTO heartbeat (timestamp, notes) VALUES (?, ?);"
    params = [timestamp, note]
    response = raw_query(query=query, params=params)

    if response:
        print("Heartbeat added.")


def get_heartbeat_table():
    """
    Return the contents of the heartbeat table.
    """
    query = "SELECT * FROM heartbeat;"
    json_data = raw_query(query=query)

    if not json_data or not json_data.get("data"):
        return pd.DataFrame()

    df = pd.DataFrame(json_data["data"])
    return df


# %%
# Main #

if __name__ == "__main__":
    print("Querying API")

    # Health Check
    print("Health Check")
    pprint_dict(health_check())

    # List Tables
    print("List Tables")
    df_tables = list_tables()
    pprint_df(df_tables)

    # Query Data
    table_name = "test_table"
    query = f"SELECT * FROM {table_name};"
    result = raw_query(query=query)
    if result and "data" in result:
        pprint_df(pd.DataFrame(result["data"]))

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
