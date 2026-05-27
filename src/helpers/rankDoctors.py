from rapidfuzz.distance import Levenshtein

from src.models.Doctor import Doctor
from src.models.RankDoctorsArgs import RankDoctorsArgs


def rankDoctors(args: RankDoctorsArgs) -> list[Doctor]:
    queryFields: dict[str, str | None] = {
        "name": args.name,
        "speciality": args.speciality,
        "location": args.location,
        "county": args.county,
        "clinic_name": args.clinic_name,
        "address": args.address,
        "education": args.education,
        "language": args.language,
    }
    activeFields = {k: v.lower() for k, v in queryFields.items() if v}

    if not activeFields:
        return args.doctors[: args.limit]

    scored: list[tuple[float, Doctor]] = []

    for doctor in args.doctors:
        similarities: list[float] = []

        for field, query in activeFields.items():
            if field == "name":
                target = f"{doctor.first_name} {doctor.last_name}".lower()
                similarities.append(Levenshtein.normalized_similarity(query, target))
            elif field == "language":
                # Score against each spoken language separately and take the
                # best, so a query for "English" matches a doctor whose list
                # contains it without being diluted by their other languages.
                if not doctor.languages:
                    similarities.append(0.0)
                else:
                    similarities.append(max(
                        Levenshtein.normalized_similarity(query, lang.lower())
                        for lang in doctor.languages
                    ))
            else:
                target = str(getattr(doctor, field)).lower()
                similarities.append(Levenshtein.normalized_similarity(query, target))

        scored.append((sum(similarities) / len(similarities), doctor))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    return [doctor for _, doctor in scored[: args.limit]]
