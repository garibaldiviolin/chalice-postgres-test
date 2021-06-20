import psycopg2
from decouple import config
from psycopg2 import ProgrammingError

from .exceptions import NotFound


def execute_query(query):
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
    cur.execute(query)

    # Make the changes to the database persistent
    conn.commit()

    rowcount = cur.rowcount
    try:
        response = cur.fetchall()
    except ProgrammingError:
        rows = []
    else:
        rows = []
        for values in response:
            row = {}
            for i, column in enumerate(cur.description):
                row[column.name] = values[i]
            rows.append(row)

    # Close communication with the database
    cur.close()
    conn.close()

    return rowcount, rows


def create_item(employee):
    fields, values = [], []
    for key, value in employee.items():
        fields.append(key)
        values.append(value)

    query = "INSERT INTO employees ({}) VALUES ({})".format(
        ", ".join(fields),
        str(values)[1:-1]
    )
    execute_query(query)


def delete_item(username):
    query = "DELETE FROM employees WHERE username = '{}'".format(
        username
    )
    rows_count = execute_query(query)
    if not rows_count:
        raise NotFound


def filter_items(params):
    query = "SELECT * FROM employees {}".format(
        params
    )
    rows_count, rows = execute_query(query)
    return rows


def get_item(username):
    query = "SELECT * FROM employees WHERE username = '{}'".format(
        username
    )
    rows_count, rows = execute_query(query)
    if not rows_count:
        raise NotFound
    return rows[0]


def update_item(username, employee):
    query = "UPDATE employees SET {} WHERE username = '{}' RETURNING *".format(
        ", ".join(
            "{} = '{}'".format(key, value)
            for key, value in employee.items()
        ),
        username
    )
    rows_count, rows = execute_query(query)
    if not rows_count:
        raise NotFound
    return rows[0]
