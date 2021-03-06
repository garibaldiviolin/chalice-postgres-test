from chalicelib.services import get_query_parameters


def test_get_query_parameters_without_parameters():
    parameters = get_query_parameters(None)
    assert parameters == {"Limit": 5}


def test_get_query_parameters_with_last_result():
    parameters = get_query_parameters({"last_result": "james_jones"})
    assert parameters == {
        'Limit': 5,
        'ExclusiveStartKey': {
            'username': 'james_jones'
        }
    }
