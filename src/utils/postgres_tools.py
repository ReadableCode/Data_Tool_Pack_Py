# %%
# Imports #

import os
import socket
import sys

import pandas as pd
from dotenv import load_dotenv
from psycopg2 import pool, sql

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.display_tools import pprint_df

# %%
# Variables #

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

dotenv_path = os.path.join(project_root, ".env")
print(dotenv_path)
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

POSTGRES_URL = os.getenv("POSTGRES_URL")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

# %%
# Connect To Postgres #


# Initialize the connection pool (adjust minconn and maxconn as needed)
POSTGRES_POOL = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=20,  # Limit connections to avoid resource waste
    host=POSTGRES_URL,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    dbname=POSTGRES_DB,
    port=POSTGRES_PORT,
)


def get_connection():
    """Get a connection from the pool."""
    return POSTGRES_POOL.getconn()


def release_connection(conn):
    """Release a connection back to the pool."""
    POSTGRES_POOL.putconn(conn)


# %%
# Functions #


def query_postgres(query):
    """Executes a given SQL query and returns a Pandas DataFrame."""
    pg_conn = None
    pg_cursor = None
    try:
        pg_conn = get_connection()
        pg_cursor = pg_conn.cursor()

        pg_cursor.execute(query)

        if not pg_cursor.description:
            raise ValueError("No data found or invalid query.")

        # Get column names
        columns = [desc[0] for desc in pg_cursor.description]

        # Convert result to DataFrame
        df = pd.DataFrame(pg_cursor.fetchall(), columns=columns)

        return df
    finally:
        if pg_cursor:
            pg_cursor.close()


def ensure_postgres_heartbeat_table():
    pg_conn = get_connection()
    pg_cursor = pg_conn.cursor()

    # Create test table
    pg_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS heartbeat (
            id SERIAL PRIMARY KEY,
            device_hostname TEXT NOT NULL,
            message TEXT NOT NULL DEFAULT 'active',
            date_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()

    print("Tables ensured.")


# %%
# Queries #


def test_ensure_postgres_heartbeat_table():
    # Ensure the table exists
    ensure_postgres_heartbeat_table()

    # Query to check if the heartbeat table exists
    query = """
    SELECT to_regclass('public.heartbeat');
    """
    result = query_postgres(query)

    print(result)

    # Assert that the table exists
    assert result.iloc[0, 0] == "heartbeat", "Heartbeat table does not exist"
    print("Test 1 passed: Heartbeat table exists.")


def test_insert_heartbeat():
    # Get the hostname of the machine
    hostname = socket.gethostname()

    # Open a connection and cursor
    pg_conn = get_connection()
    try:
        with pg_conn.cursor() as pg_cursor:
            # Insert a heartbeat entry with SQL, including the hostname
            service_name = "test_service"
            status = "active"

            query_insert = sql.SQL(
                """
                INSERT INTO heartbeat (device_hostname, message, date_time)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                RETURNING id;
            """
            )
            pg_cursor.execute(query_insert, (hostname, status))

            # Fetch the inserted id
            heartbeat_id = pg_cursor.fetchone()[0]

            # Commit the transaction
            pg_conn.commit()

        # Query to check if the heartbeat was added
        query_check = sql.SQL("SELECT * FROM heartbeat WHERE id = %s;")
        with pg_conn.cursor() as pg_cursor:
            pg_cursor.execute(query_check, (heartbeat_id,))
            result_check = pg_cursor.fetchone()

        # Assert that the inserted heartbeat exists
        assert result_check is not None, "Heartbeat entry not found"
        assert result_check[1] == hostname, "Hostname does not match"
        assert result_check[2] == status, "Status does not match"
        print("Test 2 passed: Heartbeat entry inserted and found.")
    finally:
        release_connection(pg_conn)


# %%
# Tests #

test_ensure_postgres_heartbeat_table()

# query the heartbeat table
query = """
SELECT * FROM heartbeat;

"""

result = query_postgres(query)
pprint_df(result)

test_insert_heartbeat()


# %%
