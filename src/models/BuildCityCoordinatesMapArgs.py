from pydantic import BaseModel

from src.models.Doctor import Doctor


class BuildCityCoordinatesMapArgs(BaseModel):
    doctors: list[Doctor]
