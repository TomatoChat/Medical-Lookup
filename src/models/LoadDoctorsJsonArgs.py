from pathlib import Path

from pydantic import BaseModel


class LoadDoctorsJsonArgs(BaseModel):
    filePath: Path
