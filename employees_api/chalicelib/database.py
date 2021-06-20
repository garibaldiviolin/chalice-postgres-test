import boto3
from decouple import config


def load_database():
    database_url = config("DATABASE_HOST")
    return boto3.resource("dynamodb", endpoint_url=database_url)


def load_database_table(table_name):
    database = load_database()
    return database.Table(table_name)
