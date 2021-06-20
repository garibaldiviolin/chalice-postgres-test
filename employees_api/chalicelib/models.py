from pydantic import BaseModel


class UpdateEmployee(BaseModel):
    country: str
    city: str


class Employee(UpdateEmployee):
    username: str
