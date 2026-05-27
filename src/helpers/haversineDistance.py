import math

from src.models.HaversineDistanceArgs import HaversineDistanceArgs

EARTH_RADIUS_KM = 6371.0


def haversineDistance(args: HaversineDistanceArgs) -> float:
    phi1 = math.radians(args.a.latitude)
    phi2 = math.radians(args.b.latitude)
    dPhi = math.radians(args.b.latitude - args.a.latitude)
    dLambda = math.radians(args.b.longitude - args.a.longitude)

    h = (
        math.sin(dPhi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dLambda / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(h))
