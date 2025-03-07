# %%
# Imports #

import json
import os
import sys
import time

import pandas as pd
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_utils import grandparent_dir, query_dir
from utils.display_tools import print_logger

# %%
# Creds #

dotenv_path = os.path.join(grandparent_dir, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

user_dotenv_path = os.path.join(grandparent_dir, "user.env")
if os.path.exists(user_dotenv_path):
    load_dotenv(user_dotenv_path)


# %%
# User Password Auth #


def get_snowflake_credentials(cred_env_key, role, warehouse=""):
    """
    Retrieves Snowflake credentials and establishes a connection based on
        the account type, role type, and optional warehouse.

    Args:
        cred_env_key (str): The type of Snowflake account.
        role (str): The role type to use for the connection.
        warehouse (str, optional): The Snowflake warehouse to use. Defaults to an empty string.

    Returns:
        snowflake.connector.SnowflakeConnection: A Snowflake connection object.

    Raises:
        KeyError: If the provided account type or role type does not exist in the predefined dictionaries.
        ValueError: If the Snowflake connection fails due to invalid credentials or other connection issues.
    """
    cred_env_value = os.getenv(cred_env_key)
    if cred_env_value is None:
        raise ValueError(f"Environment variable {cred_env_key} is not set.")
    creds = json.loads(cred_env_value, strict=False)

    if warehouse == "":
        warehouse = creds["warehouse"]

    print_logger(
        "Getting Credentials with:\n"
        f"User: {creds['user']}\n"
        f"Account: {creds['account']}\n"
        f"Warehouse: {creds['warehouse']}\n"
        f"Role: {role}",
        level="info",
    )

    if cred_env_key == "SNOWFLAKE_CREDS_USER":
        ctx = snowflake.connector.connect(
            user=creds["user"],
            account=creds["account"],
            warehouse=warehouse,
            role=role,
            authenticator="externalbrowser",
        )
    elif "private_key" in creds.keys():
        print("Using private key")
        private_key_data = creds["private_key"].replace("\\n", "\n").strip()

        # Load the PEM key
        private_key_pem = serialization.load_pem_private_key(
            private_key_data.encode(),
            password=None,
            backend=default_backend(),
        )

        # Convert the key to DER format
        der_private_key = private_key_pem.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        ctx = snowflake.connector.connect(
            user=creds["user"],
            account=creds["account"],
            warehouse=warehouse,
            role=role,
            private_key=der_private_key,
        )
    else:
        ctx = snowflake.connector.connect(
            user=creds["user"],
            password=creds["password"],
            account=creds["account"],
            warehouse=warehouse,
            role=role,
        )

    print_logger(
        f"Got Credentials with:\n"
        f"User: {creds['user']}\n"
        f"Account: {creds['account']}\n"
        f"Warehouse:{warehouse}\n"
        f"Role: {role}",
        level="info",
    )

    return ctx


# %%
# Get Raw Data from Snowflake #


def list_tables(cred_env_key, role, limit=10000):
    """
    Retrieves a list of tables from the specified Snowflake account and role.

    Args:
        cred_env_key (str): The type of Snowflake account.
        role (str): The role type to use for the connection.

    Returns:
        list: A list of tuples, each containing information about a table in the Snowflake account.

    Raises:
        KeyError: If the provided account type or role type does not exist in the predefined dictionaries.
        ValueError: If the Snowflake connection fails due to invalid credentials or other connection issues.
    """
    ctx = get_snowflake_credentials(cred_env_key, role)

    cs = ctx.cursor()

    try:
        cs.execute(f"SHOW TABLES LIMIT {limit}")
        tables = cs.fetchall()
    finally:
        cs.close()
    ctx.close()

    for table in tables:
        print(table)


def query_snowflake(
    cred_env_key: str,
    role: str,
    query_to_run: str,
    warehouse: str = "",
    max_retries: int = 5,
) -> pd.DataFrame:
    """
    Executes a query on Snowflake and retrieves the results, with retry logic for handling failures.

    Args:
        cred_env_key (str): The type of Snowflake account.
        role (str): The role type to use for the connection.
        query_to_run (str): The SQL query to execute.
        warehouse (str, optional): The Snowflake warehouse to use. Defaults to an empty string.
        max_retries (int, optional): The maximum number of retries in case of query failure. Defaults to 5.

    Returns:
        pd.DataFrame: A DataFrame containing the query results.
        If the query returns no data, an empty DataFrame is returned.

    Raises:
        Exception: If all retries fail or if the connection cannot be established.
    """
    print_logger(f"Running query: {query_to_run}", level="info")

    attempt = 0
    delay = 60  # Start with a 1-minute delay

    while attempt <= max_retries:
        ctx = get_snowflake_credentials(cred_env_key, role, warehouse=warehouse)
        if ctx is None:
            raise Exception("Failed to establish Snowflake connection.")

        cs = ctx.cursor()
        try:
            cs.execute(query_to_run)
            query_output = cs.fetch_pandas_all()

            if query_output is None:
                raise Exception("Snowflake returned None instead of a DataFrame.")

            if not isinstance(query_output, pd.DataFrame):
                raise Exception(
                    f"Unexpected return type from Snowflake: {type(query_output)}"
                )

            return query_output

        except Exception as e:
            attempt += 1
            if attempt > max_retries:
                raise Exception(f"Query failed after {max_retries} retries: {e}") from e

            print_logger(
                f"Snowflake query attempt {attempt} failed: {e}. Retrying in {delay / 60:.2f} minutes...",
                level="warning",
            )
            time.sleep(delay)
            delay = min(600, delay * 2)

        finally:
            cs.close()
            ctx.close()

    raise Exception("Unexpected exit from retry loop. This should never happen.")


def executeScriptsFromFile(
    cred_env_key,
    role,
    filename,
    multi_part=False,
):
    """
    Executes SQL commands from a file on Snowflake.

    Args:
        cred_env_key (str): The type of Snowflake account.
        role (str): The role type to use for the connection.
        filename (str): The name of the file containing SQL commands.
        multi_part (bool, optional): If True, the file is treated
            as containing multiple SQL commands separated by ';'. Defaults to False.

    Returns:
        Any: The result of the last executed SQL command.

    Raises:
        Exception: If any SQL command fails to execute.
    """
    # Open and read the file as a single buffer
    fd = open(os.path.join(query_dir, filename), "r")
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    if multi_part:
        sqlCommands = sqlFile.split(";")
    else:
        sqlCommands = [sqlFile]

    # Execute every command from the input file
    for command in sqlCommands:
        result = query_snowflake(cred_env_key, role, command)

    return result


# %%
