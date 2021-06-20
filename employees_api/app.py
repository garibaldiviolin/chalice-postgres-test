from botocore.exceptions import ClientError
from chalice import Chalice, Response
from pydantic.error_wrappers import ValidationError

from chalicelib.database import load_database_table
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

    table = load_database_table("Employees")

    table.put_item(Item=employee.dict())

    return Response(
        body=employee.json(),
        status_code=201
    )


@app.route("/employees", methods=["GET"])
def list_employees():
    table = load_database_table("Employees")

    parameters = get_query_parameters(app.current_request.query_params)

    if parameters.get("KeyConditionExpression"):
        results = table.query(
            **parameters
        )
    else:
        results = table.scan(**parameters)

    response = {
        "results": results["Items"]
    }
    next_results = results.get("LastEvaluatedKey")
    if next_results:
        response["last_result"] = next_results["username"]

    return response


@app.route("/employees/{username}", methods=["GET"])
def get_employee(username):
    table = load_database_table("Employees")

    try:
        response = table.get_item(Key={"username": username})
    except ClientError:
        return Response(body={"error": "internal_error"}, status_code=500)

    try:
        return Response(body=response["Item"], status_code=200)
    except KeyError:
        return Response(body={"error": "not_found"}, status_code=404)


@app.route("/employees/{username}", methods=["PUT"])
def update_employee(username):
    try:
        employee = UpdateEmployee(**app.current_request.json_body)
    except ValidationError as exc:
        return Response(
            body=exc.json(),
            status_code=400
        )

    table = load_database_table("Employees")

    response = table.update_item(
        Key={"username": username},
        UpdateExpression="set city=:city, country=:country",
        ExpressionAttributeValues={
            ":city": employee.dict()["city"],
            ":country": employee.dict()["country"],
        },
        ReturnValues="ALL_NEW"
    )
    return response["Attributes"]


@app.route("/employees/{username}", methods=["DELETE"])
def delete_employee(username):
    table = load_database_table("Employees")

    try:
        table.delete_item(
            Key={
                "username": username,
            },
            ConditionExpression="username = :v_username",
            ExpressionAttributeValues={
                ":v_username": username
            }
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return Response(body={"error": "not_found"}, status_code=404)
        else:
            return Response(body={"error": "internal_error"}, status_code=500)
    else:
        return Response(body=None, status_code=204)
