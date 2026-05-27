import json

from src.models.SaveDoctorsArgs import SaveDoctorsArgs


def saveDoctors(args: SaveDoctorsArgs) -> None:
    args.filePath.parent.mkdir(parents=True, exist_ok=True)
    payload = [doctor.model_dump(mode="json") for doctor in args.doctors]
    args.filePath.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
