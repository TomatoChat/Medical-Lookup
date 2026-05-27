import httpx

from src.models.Doctor import Doctor
from src.models.EnrichDoctorWithCoordinatesArgs import (
    EnrichDoctorWithCoordinatesArgs,
)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "peec-soda-wonderful/0.1 (geocoding)"


def enrichDoctorWithCoordinates(args: EnrichDoctorWithCoordinatesArgs) -> Doctor:
    doctor = args.doctor

    if doctor.latitude is not None and doctor.longitude is not None:
        return doctor

    query = ", ".join([
        doctor.address,
        doctor.location,
        doctor.county,
        doctor.postal_code,
        "Romania",
    ])

    response = httpx.get(
        NOMINATIM_URL,
        params={"q": query, "format": "json", "limit": 1},
        headers={"User-Agent": USER_AGENT},
        timeout=10.0,
    )
    response.raise_for_status()
    matches = response.json()

    if not matches:
        return doctor

    top = matches[0]
    return doctor.model_copy(update={
        "latitude": float(top["lat"]),
        "longitude": float(top["lon"]),
    })
