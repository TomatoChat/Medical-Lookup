from pydantic import BaseModel, Field


class Doctor(BaseModel):
    first_name: str
    last_name: str
    clinic_name: str
    location: str
    speciality: str
    address: str
    phone: str
    email: str
    postal_code: str
    county: str
    years_experience: int
    education: str
    languages: list[str] = Field(default_factory=list)
    availability: str
    rating: float
    latitude: float | None = None
    longitude: float | None = None
