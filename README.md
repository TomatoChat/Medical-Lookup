# Medical-Lookup

A small FastAPI service that ingests Romanian doctor records, enriches them
with geocoded city coordinates, and exposes search endpoints — both a
parameter-based filter and a natural-language query backed by an LLM.

## Run

```bash
uv sync
uv run uvicorn main:app --reload
```

The app reads `OPENAI_API_KEY` from the environment or from a `.env` file in
the working directory. Without it, `/search-query` will fail; `/search` and
`/ingest-doctors` work without an API key.

Default URL: <http://127.0.0.1:8000> — interactive docs at `/docs`.

## Endpoints

| Method | Path              | Description                                              |
| ------ | ----------------- | -------------------------------------------------------- |
| POST   | `/ingest-doctors` | Read `data/healthcare_data.json`, geocode every unique `(location, county)` pair via Nominatim, write enriched rows to `data/doctors.json`. |
| GET    | `/search`         | Fuzzy-rank doctors using any combination of `name`, `speciality`, `location`, `county`, `clinic_name`, `address`, `education`, `language`. Requires `limit`. |
| POST   | `/search-query`   | Natural-language question (e.g. *"Find me 2 cardiologists in Cluj-Napoca who speak Hungarian"*); an LLM parses it into the same fields as `/search` and runs the ranker, with closest-city fallback when no in-city match exists. |

## How filtering works

### `POST /ingest-doctors`

1. Read `data/healthcare_data.json` into a list of `Doctor` records.
2. Build the set of unique `(location, county)` pairs.
3. For each unique pair, call Nominatim with `"{location}, {county}, Romania"`
   and a 1 req/s rate limit (per Nominatim's usage policy), collecting a
   `(latitude, longitude)` per pair. Failures are tolerated — the doctor is
   kept without coordinates.
4. Copy each doctor with their city's coordinates filled in.
5. Write the enriched list to `data/doctors.json`.

### `GET /search`

A pure ranker — every doctor is scored against the active filters and the top
`limit` are returned.

1. 404 if `data/doctors.json` is missing (run `/ingest-doctors` first).
2. Load the full doctor list.
3. Collect the active filters from query params (`name`, `speciality`,
   `location`, `county`, `clinic_name`, `address`, `education`, `language`).
   Anything `None` is ignored.
4. If no filters are active, return the first `limit` doctors unchanged.
5. Otherwise score each doctor against every active filter (see
   [Scoring](#scoring) below), average the per-field scores, sort
   descending, return the top `limit`.

### `POST /search-query`

The LLM extracts structured fields from the natural-language question, then a
multi-stage pipeline applies hard filters first and falls back progressively
when nothing matches.

1. 404 if `data/doctors.json` is missing.
2. **Parse the question** with `gpt-4.1-mini` via OpenAI's structured-output
   `parse`, producing a `DoctorSearchQuery` with the same fields as `/search`
   plus a `limit`.
3. Load the full doctor list.
4. **Hard pre-filter** (substring, case-insensitive):
   - If `speciality` is set, keep only doctors whose `speciality` contains
     it as a substring.
   - If `location` is set, keep only doctors whose `location` contains it
     as a substring.
5. **Primary path** — if any candidates survived the pre-filter, rank them
   with the [scorer](#scoring) using **all** extracted fields (including the
   speciality and location used for pre-filtering — they act as tiebreakers
   within the surviving set). Return the top `limit`.
6. **Fallback 1** — pre-filter eliminated everyone *and* no speciality was
   requested: rank the entire doctor list with every field except
   `speciality`, return the top `limit`. (Without a speciality there's no
   sensible way to narrow the pool further.)
7. **Fallback 2** — speciality was requested but pre-filter eliminated
   everyone:
   1. Re-scan all doctors for those whose `speciality` substring-matches
      (`specialityMatches`).
   2. If `specialityMatches` is empty, rank the entire doctor list using
      only `speciality` and `location`. This surfaces the closest-named
      speciality (e.g. *"Cardiologie"* still finds *"Cardiology"*).
   3. If no `location` was requested, return the first `limit` of
      `specialityMatches` directly (no further ranking — they all match
      the speciality and there's nothing left to discriminate on).
   4. Otherwise, find anchor coordinates for the requested location:
      - Use the coordinates of any existing doctor in that city, *or*
      - Call Nominatim to geocode the city on the fly.
   5. If an anchor exists, return the geographically-closest doctors from
      `specialityMatches` (Haversine distance). If not, return the first
      `limit` of `specialityMatches`.

### Scoring

When the ranker is invoked, each active filter contributes one similarity in
`[0, 1]`; the per-field scores are averaged and doctors are returned in
descending order of the average.

For a single `(query, target)` pair:

1. **Exact lowercased substring match → 1.0.** So `"Carol Davila"` scores
   perfectly against `"Carol Davila University of Medicine and Pharmacy"`,
   and `"Cluj-Napoca"` against `"Clinica Cluj-Napoca Care"`.
2. **Otherwise**, the better of `rapidfuzz.fuzz.partial_ratio` (best-aligned
   substring) and `token_set_ratio` (token-overlap, order-independent),
   normalized to `[0, 1]`. This lets `"Cardiologie"` (RO) match
   `"Cardiology"` (EN) at ~0.95 and handles word reordering like
   `"Matei Tudor"` ↔ `"Tudor Matei"`.

Field-specific handling:

- **`name`** — scored against `"{first_name} {last_name}"`.
- **`language`** — `languages` is a list per doctor; the score is the
  **max** across that list, so a query for `"English"` is not diluted by
  the doctor's other languages. Empty list → 0.0.
- **All others** — scored against the doctor's field of the same name.

Note that `/search` is a *ranker*, not a strict filter: when fewer than
`limit` doctors match every criterion perfectly, near-misses fill the
remaining slots ordered by their averaged similarity. `/search-query` adds
the hard pre-filter on speciality and location before ranking, so its top
results are guaranteed to match those two fields when any such doctor
exists.

## Processing time

Measured locally against the bundled dataset (7029 doctors, 42 unique
cities).

| Operation                                       | Time              |
| ----------------------------------------------- | ----------------- |
| `POST /ingest-doctors` (full pipeline)          | ~45 s             |
| &nbsp;&nbsp;↳ Nominatim geocoding (42 cities @ 1 req/s) | ~42 s     |
| `GET /search` (hybrid rank, 7029 rows)          | 45–60 ms          |
| `POST /search-query` (LLM parse + rank)         | 1.8–3.3 s (OpenAI latency dominates) |
