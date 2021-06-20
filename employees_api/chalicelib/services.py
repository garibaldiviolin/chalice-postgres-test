from .models import Employee


def get_query_parameters(query_params):
    query_params = query_params if query_params else {}
    sql_parameters = ""
    try:
        limit = query_params.pop("limit")
    except KeyError:
        limit = 50
    else:
        limit = limit if limit.isnumeric() is True and int(limit) < 50 else 50

    filters = {}

    employee_schema = Employee.schema()
    for field, value in query_params.items():
        if field in employee_schema["properties"].keys():
            filters[field] = value

    if filters:
        sql_parameters += " WHERE "
        sql_parameters += " AND ".join(
            "{} = '{}'".format(key, value)
            for key, value in filters.items()
        )

    sql_parameters += "LIMIT {}".format(limit)
    return sql_parameters
