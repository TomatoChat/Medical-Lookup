from pydantic import BaseModel


class GeocodeLocationArgs(BaseModel):
    location: str
