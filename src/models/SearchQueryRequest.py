from pydantic import BaseModel


class SearchQueryRequest(BaseModel):
    question: str
