from pathlib import Path

from pydantic import BaseModel

from src.models.Doctor import Doctor


class SaveDoctorsArgs(BaseModel):
    doctors: list[Doctor]
    filePath: Path
