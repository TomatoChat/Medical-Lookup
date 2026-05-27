import time

from src.helpers.geocodeLocation import geocodeLocation
from src.models.BuildCityCoordinatesMapArgs import (
    BuildCityCoordinatesMapArgs,
)
from src.models.Coordinates import Coordinates
from src.models.GeocodeLocationArgs import GeocodeLocationArgs

# Nominatim's public usage policy is 1 request/sec.
NOMINATIM_RATE_LIMIT_SECONDS = 1.0


def buildCityCoordinatesMap(
    args: BuildCityCoordinatesMapArgs,
) -> dict[tuple[str, str], Coordinates]:
    uniqueCities = {(doctor.location, doctor.county) for doctor in args.doctors}

    cityCoords: dict[tuple[str, str], Coordinates] = {}
    for location, county in uniqueCities:
        try:
            coords = geocodeLocation(
                GeocodeLocationArgs(location=f"{location}, {county}")
            )
        except Exception:
            coords = None
        if coords is not None:
            cityCoords[(location, county)] = coords
        time.sleep(NOMINATIM_RATE_LIMIT_SECONDS)

    return cityCoords
