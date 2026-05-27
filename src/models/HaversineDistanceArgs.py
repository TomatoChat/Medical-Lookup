from pydantic import BaseModel

from src.models.Coordinates import Coordinates


class HaversineDistanceArgs(BaseModel):
    a: Coordinates
    b: Coordinates
