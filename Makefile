create-database:
	pipenv run python employees_api/create_database.py

run-local-chalice:
	cd employees_api && pipenv run chalice local --port 8001

test:
	pipenv run pytest -vvs
