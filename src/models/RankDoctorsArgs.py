from pydantic import BaseModel, Field

from src.models.Doctor import Doctor


class RankDoctorsArgs(BaseModel):
    doctors: list[Doctor]
    limit: int = Field(ge=1)
    name: str | None = None
    speciality: str | None = None
    location: str | None = None
    county: str | None = None
    clinic_name: str | None = None
    address: str | None = None
    education: str | None = None
    language: str | None = None
