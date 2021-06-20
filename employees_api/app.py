from chalice import Chalice, Response
from pydantic.error_wrappers import ValidationError
from psycopg2.errors import UniqueViolation

from chalicelib.database import (
    create_item,
    delete_item,
    filter_items,
    get_item,
    update_item,
)
from chalicelib.exceptions import NotFound
from chalicelib.models import UpdateEmployee, Employee
from chalicelib.services import get_query_parameters

app = Chalice(app_name="employees_api")


@app.route("/employees", methods=["POST"])
def create_employee():
    try:
        employee = Employee(**app.current_request.json_body)
    except ValidationError as exc:
        return Response(
            body=exc.json(),
            status_code=400
        )

    try:
        create_item(employee.dict())
    except UniqueViolation:
        return Response(
            body={"error": "employee already exists"},
            status_code=400
        )

    return Response(
        body=employee.json(),
        status_code=201
    )


@app.route("/employees", methods=["GET"])
def list_employees():
    parameters = get_query_parameters(app.current_request.query_params)

    results = filter_items(parameters)

    response = {
        "results": results
    }

    return response


@app.route("/employees/{username}", methods=["GET"])
def get_employee(username):
    try:
        employee = get_item(username)
    except NotFound:
        return Response(body={"error": "not_found"}, status_code=404)

    return Response(body=employee, status_code=200)


@app.route("/employees/{username}", methods=["PUT"])
def update_employee(username):
    try:
        employee = UpdateEmployee(**app.current_request.json_body)
    except ValidationError as exc:
        return Response(
            body=exc.json(),
            status_code=400
        )

    try:
        response = update_item(
            username,
            employee.dict()
        )
    except NotFound:
        return Response(body={"error": "not_found"}, status_code=404)
    return response


@app.route("/employees/{username}", methods=["DELETE"])
def delete_employee(username):
    try:
        delete_item(username)
    except NotFound:
        return Response(body={"error": "not_found"}, status_code=404)
    else:
        return Response(body=None, status_code=204)
