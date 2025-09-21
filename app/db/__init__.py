from time import sleep
import duckdb
from duckdb import DuckDBPyConnection
import os
from typing import Any


create_users_table: str = """
CREATE TABLE IF NOT EXISTS Users (
    id UUID PRIMARY KEY,
    name VARCHAR,
    admin BOOLEAN,
    password VARCHAR,
    create_time TIMESTAMP
);
"""

create_machines_table: str = """
CREATE TABLE IF NOT EXISTS Machines (
    id UUID PRIMARY KEY,
    hostname VARCHAR,
    created_time TIMESTAMP,
    condition INTEGER,
    special_note VARCHAR
);
"""

create_logs_table: str = """
CREATE TABLE IF NOT EXISTS Logs (
    logged_at TIMESTAMP,
    user_id UUID REFERENCES Users(id),
    machine_id UUID REFERENCES Machines(id),
    active BOOLEAN,
    prompts JSON
);
"""

create_logs_time_index: str = """
CREATE INDEX IF NOT EXISTS logs_time_idx ON Logs ("logged_at");
"""


def create_database(database: str) -> None:
    conn: DuckDBPyConnection = duckdb.connect(database)
    conn.execute(create_users_table)
    conn.execute(create_machines_table)
    conn.execute(create_logs_table)
    conn.execute(create_logs_time_index)
    conn.close()


def get_write_conn(database: str) -> DuckDBPyConnection:
    conn: DuckDBPyConnection = duckdb.connect(database)
    return conn


def get_read_conn(database: str) -> DuckDBPyConnection:
    try:
        conn: DuckDBPyConnection = duckdb.connect(database, read_only=True)
        return conn
    except duckdb.Error:
        sleep(2)
        return get_read_conn(database)


def load_csv_data(
    conn: DuckDBPyConnection, users_csv_path: str, machines_csv_path: str
) -> None:
    """
    Loads user and machine data from CSV files into existing DuckDB tables.

    This function first verifies that the 'Users' and 'Machines' tables exist
    in the database. If they do not, the function will fail with an error.

    Args:
        con: An active DuckDB connection object.
        users_csv_path (str): The file path to the users CSV data.
        machines_csv_path (str): The file path to the machines CSV data.

    Raises:
        FileNotFoundError: If either of the provided CSV file paths do not exist.
        ValueError: If either the 'Users' or 'Machines' tables do not exist in the connected database.
        duckdb.Error: For other potential database errors during data insertion.
    """
    if not os.path.exists(users_csv_path):
        raise FileNotFoundError(f"Error: The file '{users_csv_path}' was not found.")
    if not os.path.exists(machines_csv_path):
        raise FileNotFoundError(f"Error: The file '{machines_csv_path}' was not found.")

    tables_result: list[Any] = conn.execute(
        "SELECT table_name FROM duckdb_tables()"
    ).fetchall()
    existing_tables: set[str] = {table[0].lower() for table in tables_result}

    if "users" not in existing_tables:
        raise ValueError(
            "Table 'Users' does not exist. Please initialize the database first."
        )
    if "machines" not in existing_tables:
        raise ValueError(
            "Table 'Machines' does not exist. Please initialize the database first."
        )

    try:
        conn.execute(
            "INSERT INTO Users SELECT * FROM read_csv_auto(?, header=True)",
            [users_csv_path],
        )

    except duckdb.Error:
        pass

    try:
        conn.execute(
            "INSERT INTO Machines SELECT * FROM read_csv_auto(?, header=True)",
            [machines_csv_path],
        )

    except duckdb.Error:
        pass
