import json
from operator import itemgetter
from unittest.mock import patch, Mock

import pytest
from botocore.exceptions import ClientError


def test_create_employee(lambda_client, employee, employees_url):
    response = lambda_client.http.post(
        employees_url,
        body=json.dumps(employee),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 201
    assert response.json_body == employee


def test_create_employee_without_fields(lambda_client, employees_url):
    response = lambda_client.http.post(
        employees_url,
        body="{}",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert response.json_body == [
        {
            "loc": ["country"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["city"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["username"],
            "msg": "field required",
            "type": "value_error.missing"
        },
    ]


def test_list_employees(lambda_client, employees_url, database_employee):
    response = lambda_client.http.get(
        employees_url,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert response.json_body == {
        "results": [{
            "city": "Houston",
            "username": "john_dunbar",
            "country": "United States of America"
        }]
    }


def test_list_employees_with_more_results(lambda_client, employees_url,
                                          six_database_employee):
    response = lambda_client.http.get(
        employees_url,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert response.json_body["last_result"] == "0"
    assert len(response.json_body["results"]) == 5
    first_item = response.json_body["results"][0]
    assert "city" in first_item
    assert "country" in first_item
    assert "username" in first_item


def test_list_employees_with_invalid_filter(lambda_client, employees_url,
                                            database_employee):
    response = lambda_client.http.get(
        employees_url + "?country=United%20States%20of%20America&city=Houston",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert response.json_body == {
        "results": [
            {
                "city": "Houston",
                "username": "john_dunbar",
                "country": "United States of America"
            }
        ]
    }


@pytest.mark.parametrize(
    "query_strings, expected_response",
    (
        ("?username=john_dunbar", [
            {
                "city": "Houston",
                "username": "john_dunbar",
                "country": "United States of America"
            }
        ]),
        ("?username=john", [])
    )
)
def test_list_employees_with_valid_filter(query_strings, expected_response,
                                          lambda_client, employees_url,
                                          database_employee):
    response = lambda_client.http.get(
        employees_url + query_strings,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert response.json_body == {
        "results": expected_response
    }


def test_get_employee(lambda_client, database_employee, employee,
                      employee_url):
    response = lambda_client.http.get(
        employee_url,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert response.json_body == employee


@patch("boto3.resource")
def test_get_employee_with_internal_error(boto3_resource_mock, lambda_client,
                                          database_employee, employee,
                                          employee_url):
    table_mock = Mock()
    table_mock.get_item = Mock()
    table_mock.get_item.side_effect = ClientError(
        error_response={},
        operation_name=None,
    )
    dynamodb_mock = Mock()
    dynamodb_mock.Table = Mock(return_value=table_mock)
    boto3_resource_mock.return_value = dynamodb_mock

    response = lambda_client.http.get(
        employee_url,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 500
    assert response.json_body == {"error": "internal_error"}


def test_get_employee_not_found(lambda_client, database_employee, employee,
                                inexistent_employee_url):
    response = lambda_client.http.get(
        inexistent_employee_url,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 404
    assert response.json_body == {"error": "not_found"}


def test_update_employee(lambda_client, employee, employee_url):
    response = lambda_client.http.put(
        employee_url,
        body=json.dumps(employee),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert response.json_body == employee


def test_update_employee_without_fields(lambda_client, employee, employee_url):
    response = lambda_client.http.put(
        employee_url,
        body="{}",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert response.json_body == [
        {
            "loc": ["country"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["city"],
            "msg": "field required",
            "type": "value_error.missing"
        },
    ]


def test_delete_employee(lambda_client, database_employee, employee,
                         employee_url):
    response = lambda_client.http.delete(
        employee_url,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 204
    assert response.json_body is None


def test_delete_employee_not_found(lambda_client, employee,
                                   inexistent_employee_url):
    response = lambda_client.http.delete(
        inexistent_employee_url,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 404
    assert response.json_body == {"error": "not_found"}


@patch("boto3.resource")
def test_delete_employee_internal_error(boto3_resource_mock, lambda_client,
                                        employee, inexistent_employee_url):
    table_mock = Mock()
    table_mock.delete_item = Mock()
    table_mock.delete_item.side_effect = ClientError(
        error_response={"Error": {"Code": "InternalError"}},
        operation_name=None,
    )
    dynamodb_mock = Mock()
    dynamodb_mock.Table = Mock(return_value=table_mock)
    boto3_resource_mock.return_value = dynamodb_mock

    response = lambda_client.http.delete(
        inexistent_employee_url,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 500
    assert response.json_body == {"error": "internal_error"}
