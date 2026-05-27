from pydantic import BaseModel, Field

from src.models.Coordinates import Coordinates
from src.models.Doctor import Doctor


class FindClosestDoctorsArgs(BaseModel):
    doctors: list[Doctor]
    target: Coordinates
    speciality: str | None = None
    limit: int = Field(ge=1)
