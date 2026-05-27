from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from src.helpers.loadDoctorsJson import loadDoctorsJson
from src.helpers.rankDoctors import rankDoctors
from src.models.Doctor import Doctor
from src.models.LoadDoctorsJsonArgs import LoadDoctorsJsonArgs
from src.models.RankDoctorsArgs import RankDoctorsArgs

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DOCTORS_FILE = DATA_DIR / "doctors.json"

router = APIRouter()


@router.get("/search")
def searchDoctors(
    limit: int = Query(..., ge=1, description="Number of doctors to return"),
    name: str | None = None,
    speciality: str | None = None,
    location: str | None = None,
    county: str | None = None,
    clinic_name: str | None = None,
    address: str | None = None,
    education: str | None = None,
) -> list[Doctor]:
    if not DOCTORS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Doctors data not found. Run /ingest-doctors first.",
        )

    doctors = loadDoctorsJson(LoadDoctorsJsonArgs(filePath=DOCTORS_FILE))
    return rankDoctors(RankDoctorsArgs(
        doctors=doctors,
        limit=limit,
        name=name,
        speciality=speciality,
        location=location,
        county=county,
        clinic_name=clinic_name,
        address=address,
        education=education,
    ))
