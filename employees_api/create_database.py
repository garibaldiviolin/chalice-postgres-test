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

    # Drop database, if it exists, before creating a new one
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
        CREATE TABLE "employees" (
            "username" text NOT NULL UNIQUE,
            "city" text NOT NULL, "country" text NOT NULL
        );
        CREATE INDEX "employees_username_451f2112_like" ON "employees" (
            "username" text_pattern_ops
        );
        CREATE INDEX "employees_city_1b905c49" ON "employees" ("city");
        CREATE INDEX "employees_city_1b905c49_like" ON "employees" (
            "city" text_pattern_ops
        );
        CREATE INDEX "employees_country_bd071a73" ON "employees" ("country");
        CREATE INDEX "employees_country_bd071a73_like" ON "employees" (
            "country" text_pattern_ops
        );
    """)

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()


if __name__ == "__main__":
    create_database()
