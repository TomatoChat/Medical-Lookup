from src.helpers.haversineDistance import haversineDistance
from src.models.Coordinates import Coordinates
from src.models.Doctor import Doctor
from src.models.FindClosestDoctorsArgs import FindClosestDoctorsArgs
from src.models.HaversineDistanceArgs import HaversineDistanceArgs


def findClosestDoctors(args: FindClosestDoctorsArgs) -> list[Doctor]:
    candidates = args.doctors

    if args.speciality:
        needle = args.speciality.lower()
        candidates = [d for d in candidates if needle in d.speciality.lower()]

    geocoded = [
        d for d in candidates
        if d.latitude is not None and d.longitude is not None
    ]

    def distanceKm(doctor: Doctor) -> float:
        return haversineDistance(HaversineDistanceArgs(
            a=args.target,
            b=Coordinates(latitude=doctor.latitude, longitude=doctor.longitude),
        ))

    geocoded.sort(key=distanceKm)
    return geocoded[: args.limit]
