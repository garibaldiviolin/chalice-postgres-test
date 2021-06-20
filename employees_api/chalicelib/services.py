from boto3.dynamodb.conditions import Key


def get_query_parameters(query_params):
    query_params = query_params or {}

    parameters = {
        "Limit": 5,
    }

    for query_param in query_params:
        if query_param in ["username", "city", "country"]:
            if "KeyConditionExpression" not in parameters:
                parameters["KeyConditionExpression"] = Key(query_param).eq(
                    query_params[query_param]
                )
            else:
                parameters["KeyConditionExpression"] &= Key(query_param).eq(
                    query_params[query_param]
                )
        if query_param in ["city", "country"]:
            parameters["IndexName"] = "RegionIndex"

    last_result = query_params.get("last_result")
    if last_result:
        parameters["ExclusiveStartKey"] = {
            "username": last_result
        }

    return parameters
