from rapidfuzz import fuzz

from src.models.Doctor import Doctor
from src.models.RankDoctorsArgs import RankDoctorsArgs


def _score(query: str, target: str) -> float:
    """Hybrid string similarity in [0, 1].

    Exact lowercased substring → 1.0; otherwise the better of `partial_ratio`
    (best-aligned substring) and `token_set_ratio` (token overlap, ignoring
    order and duplicates). Whole-string Levenshtein would unfairly punish
    cases like query "Carol Davila" against target
    "Carol Davila University of Medicine and Pharmacy" — the query appears
    verbatim but the long tail of unmatched characters drags the score down.
    """
    if not target:
        return 0.0
    if query in target:
        return 1.0
    return max(
        fuzz.partial_ratio(query, target),
        fuzz.token_set_ratio(query, target),
    ) / 100.0


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
                similarities.append(_score(query, target))
            elif field == "language":
                # Score against each spoken language separately and take the
                # best, so a query for "English" matches a doctor whose list
                # contains it without being diluted by their other languages.
                if not doctor.languages:
                    similarities.append(0.0)
                else:
                    similarities.append(max(
                        _score(query, lang.lower())
                        for lang in doctor.languages
                    ))
            else:
                target = str(getattr(doctor, field)).lower()
                similarities.append(_score(query, target))

        scored.append((sum(similarities) / len(similarities), doctor))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    return [doctor for _, doctor in scored[: args.limit]]
