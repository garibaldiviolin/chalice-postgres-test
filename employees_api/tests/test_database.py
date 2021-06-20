from unittest.mock import Mock, patch

from chalicelib.database import load_database, load_database_table


@patch("boto3.resource")
@patch("chalicelib.database.config")
def test_load_database(decouple_config_mock, boto3_resource_mock):
    database_url = "http://nice_database_url"
    decouple_config_mock.return_value = database_url
    database_mock = Mock()
    boto3_resource_mock.return_value = database_mock

    assert load_database() == database_mock

    decouple_config_mock.assert_called_once_with("DATABASE_URL")
    boto3_resource_mock.assert_called_once_with(
        "dynamodb",
        endpoint_url=database_url,
    )


@patch("chalicelib.database.load_database")
def test_load_database_table(load_database_mock):
    database_mock = Mock()
    table_mock = Mock()
    database_mock.Table = Mock(return_value=table_mock)
    load_database_mock.return_value = database_mock

    table_name = "NiceTable"
    assert load_database_table(table_name) == table_mock

    load_database_mock.assert_called_once_with()
    database_mock.Table.assert_called_once_with(table_name)
