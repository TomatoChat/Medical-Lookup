from pathlib import Path

from fastapi import APIRouter

from src.helpers.buildCityCoordinatesMap import buildCityCoordinatesMap
from src.helpers.loadDoctorsJson import loadDoctorsJson
from src.helpers.saveDoctors import saveDoctors
from src.models.BuildCityCoordinatesMapArgs import (
    BuildCityCoordinatesMapArgs,
)
from src.models.LoadDoctorsJsonArgs import LoadDoctorsJsonArgs
from src.models.SaveDoctorsArgs import SaveDoctorsArgs

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SOURCE_FILE = DATA_DIR / "healthcare_data.json"
TARGET_FILE = DATA_DIR / "doctors.json"

router = APIRouter()


@router.post("/ingest-doctors")
def ingestDoctors() -> dict[str, int | str]:
    doctors = loadDoctorsJson(LoadDoctorsJsonArgs(filePath=SOURCE_FILE))

    cityCoords = buildCityCoordinatesMap(
        BuildCityCoordinatesMapArgs(doctors=doctors)
    )

    enriched = []
    geocoded = 0
    for doctor in doctors:
        coords = cityCoords.get((doctor.location, doctor.county))
        if coords is None:
            enriched.append(doctor)
            continue
        enriched.append(doctor.model_copy(update={
            "latitude": coords.latitude,
            "longitude": coords.longitude,
        }))
        geocoded += 1

    saveDoctors(SaveDoctorsArgs(doctors=enriched, filePath=TARGET_FILE))
    return {
        "ingested": len(enriched),
        "uniqueCities": len(cityCoords),
        "geocoded": geocoded,
        "savedTo": str(TARGET_FILE),
    }
