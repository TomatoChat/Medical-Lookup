from pydantic import BaseModel


class ParseDoctorQueryArgs(BaseModel):
    question: str
