from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.helpers.findClosestDoctors import findClosestDoctors
from src.helpers.geocodeLocation import geocodeLocation
from src.helpers.loadDoctorsJson import loadDoctorsJson
from src.helpers.parseDoctorQuery import parseDoctorQuery
from src.helpers.rankDoctors import rankDoctors
from src.models.Coordinates import Coordinates
from src.models.Doctor import Doctor
from src.models.FindClosestDoctorsArgs import FindClosestDoctorsArgs
from src.models.GeocodeLocationArgs import GeocodeLocationArgs
from src.models.LoadDoctorsJsonArgs import LoadDoctorsJsonArgs
from src.models.ParseDoctorQueryArgs import ParseDoctorQueryArgs
from src.models.RankDoctorsArgs import RankDoctorsArgs
from src.models.SearchQueryRequest import SearchQueryRequest

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DOCTORS_FILE = DATA_DIR / "doctors.json"

router = APIRouter()


@router.post("/search-query")
def searchQuery(request: SearchQueryRequest) -> list[Doctor]:
    if not DOCTORS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Doctors data not found. Run /ingest-doctors first.",
        )

    query = parseDoctorQuery(ParseDoctorQueryArgs(question=request.question))
    doctors = loadDoctorsJson(LoadDoctorsJsonArgs(filePath=DOCTORS_FILE))

    candidates = doctors
    if query.speciality:
        needle = query.speciality.lower()
        candidates = [d for d in candidates if needle in d.speciality.lower()]
    if query.location:
        needle = query.location.lower()
        candidates = [d for d in candidates if needle in d.location.lower()]

    if candidates:
        return rankDoctors(RankDoctorsArgs(
            doctors=candidates,
            limit=query.limit,
            name=query.name,
            speciality=query.speciality,
            location=query.location,
            county=query.county,
            clinic_name=query.clinic_name,
            address=query.address,
            education=query.education,
        ))

    # Fallback 1: profession only
    if not query.speciality:
        return rankDoctors(RankDoctorsArgs(
            doctors=doctors,
            limit=query.limit,
            name=query.name,
            location=query.location,
            county=query.county,
            clinic_name=query.clinic_name,
            address=query.address,
            education=query.education,
        ))

    needle = query.speciality.lower()
    specialityMatches = [d for d in doctors if needle in d.speciality.lower()]

    if not specialityMatches:
        return rankDoctors(RankDoctorsArgs(
            doctors=doctors,
            limit=query.limit,
            speciality=query.speciality,
            location=query.location,
        ))

    if not query.location:
        return specialityMatches[: query.limit]

    # Fallback 2: closest doctor with that profession.
    # Try to anchor on coords of any existing doctor in the requested city;
    # if none, geocode the city via Nominatim.
    locNeedle = query.location.lower()
    target: Coordinates | None = None
    for d in doctors:
        if locNeedle in d.location.lower() and d.latitude is not None and d.longitude is not None:
            target = Coordinates(latitude=d.latitude, longitude=d.longitude)
            break

    if target is None:
        target = geocodeLocation(GeocodeLocationArgs(location=query.location))

    if target is None:
        return specialityMatches[: query.limit]

    closest = findClosestDoctors(FindClosestDoctorsArgs(
        doctors=specialityMatches,
        target=target,
        limit=query.limit,
    ))
    return closest or specialityMatches[: query.limit]
