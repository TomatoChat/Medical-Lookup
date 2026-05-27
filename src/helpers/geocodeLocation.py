import httpx

from src.models.Coordinates import Coordinates
from src.models.GeocodeLocationArgs import GeocodeLocationArgs

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "peec-soda-wonderful/0.1 (geocoding)"


def geocodeLocation(args: GeocodeLocationArgs) -> Coordinates | None:
    response = httpx.get(
        NOMINATIM_URL,
        params={"q": f"{args.location}, Romania", "format": "json", "limit": 1},
        headers={"User-Agent": USER_AGENT},
        timeout=10.0,
    )
    response.raise_for_status()
    matches = response.json()

    if not matches:
        return None

    return Coordinates(
        latitude=float(matches[0]["lat"]),
        longitude=float(matches[0]["lon"]),
    )
