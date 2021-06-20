import psycopg2
from decouple import config
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql


def create_database():
    # Connect to an existing database
    conn = psycopg2.connect(
        "dbname=postgres host={} user={} password={} ".format(
            config("DATABASE_HOST"),
            config("DATABASE_USER"),
            config("DATABASE_PASSWORD"),
        )
    )

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cur = conn.cursor()

    cur.execute(sql.SQL("""
        DROP DATABASE IF EXISTS employees;
    """))

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute("""
        CREATE DATABASE employees;
    """)

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    # Connect to an existing database
    conn = psycopg2.connect(
        "dbname=employees host={} user={} password={}".format(
            config("DATABASE_HOST"),
            config("DATABASE_USER"),
            config("DATABASE_PASSWORD"),
        )
    )

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute("""
        CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);
    """)

    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no more SQL injections!)
    cur.execute(
        "INSERT INTO test (num, data) VALUES (%s, %s)",
        (100, "abc'def")
    )

    # Query the database and obtain data as Python objects
    cur.execute("SELECT * FROM test;")
    cur.fetchone()

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()


if __name__ == "__main__":
    create_database()
