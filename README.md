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
| GET    | `/search`         | Fuzzy-rank doctors using any combination of `name`, `speciality`, `location`, `county`, `clinic_name`, `address`, `education`. Requires `limit`. |
| POST   | `/search-query`   | Natural-language question (e.g. *"Find me 2 cardiologists in Cluj-Napoca"*); an LLM parses it into the same fields as `/search` and runs the ranker, with closest-city fallback when no in-city match exists. |

The `languages` field is present on each doctor record but is **not** exposed
as a query parameter on `/search` and is **not** extracted by the LLM in
`/search-query` — filtering by spoken language is not supported.

## Processing time

Measured locally against the bundled dataset (7029 doctors, 42 unique
cities).

| Operation                                       | Time              |
| ----------------------------------------------- | ----------------- |
| `POST /ingest-doctors` (full pipeline)          | ~45 s             |
| &nbsp;&nbsp;↳ Nominatim geocoding (42 cities @ 1 req/s) | ~42 s     |
| `GET /search` (filter + fuzzy rank, 7029 rows)  | 30–70 ms          |
| `POST /search-query` (LLM parse + rank)         | 2–5 s (OpenAI latency dominates) |
