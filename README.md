# chalice-postgres-test
A test using Chalice (Python framework for AWS Lambda) and PostgreSQL.

## Requirements
- [Python3+](https://www.python.org/downloads/);
- [Pipenv](https://github.com/pypa/pipenv);
- [PostgreSQL 13.2](https://www.postgresql.org/).

## Development
1) Run `make create-database`;
2) Run `make run-local-chalice` to start the chalice development server.

## Production
- Fill `DATABASE_HOST`, `DATABASE_USER` and `DATABASE_PASSWORD` values in `employees_api/.chalice/config.json`.
