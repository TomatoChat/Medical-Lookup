import json

from src.models.Doctor import Doctor
from src.models.LoadDoctorsJsonArgs import LoadDoctorsJsonArgs


def loadDoctorsJson(args: LoadDoctorsJsonArgs) -> list[Doctor]:
    raw = json.loads(args.filePath.read_text(encoding="utf-8"))

    # Real-world equivalent: fetch the same payload from an upstream API.
    # Swap the two lines above for something like the block below once the
    # endpoint is available — the local JSON is only here to simulate it.
    #
    # import httpx
    # response = httpx.get(
    #     "https://api.example.com/healthcare/doctors",
    #     headers={"Authorization": f"Bearer {API_TOKEN}"},
    #     timeout=30.0,
    # )
    # response.raise_for_status()
    # raw = response.json()

    return [Doctor(**item) for item in raw]
