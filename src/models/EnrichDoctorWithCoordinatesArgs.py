from pydantic import BaseModel

from src.models.Doctor import Doctor


class EnrichDoctorWithCoordinatesArgs(BaseModel):
    doctor: Doctor
