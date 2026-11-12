# Data Processing API — Docker Packaging Exercise

An **existing starter application** for a hands-on container packaging optimization task. The code is supplied as a sample repository for your recording; it is **not an externally published GitHub project**. It is licensed under the [MIT License](LICENSE).

## What it does

- FastAPI REST endpoints: `GET /health`, `GET /db/health`, `POST /sales/summary`.
- Processes sales CSVs with Pandas and NumPy, ignoring non-completed orders.
- Optionally saves results into PostgreSQL using **psycopg2**, which is built against native PostgreSQL libraries.
- Includes six sample orders and automated tests.

### Dependency versions

| Dependency | Version |
| --- | --- |
| Python | 3.12 |
| fastapi | 0.115.6 |
| uvicorn | 0.34.0 |
| pandas | 2.2.3 |
| numpy | 1.26.4 |
| psycopg2 | 2.9.10 |

## Quick start: local Python

Requires Python 3.12, a working C compiler, `pg_config`, and PostgreSQL client headers to build `psycopg2` from source. On Debian, install `build-essential libpq-dev`; on macOS, install PostgreSQL development tools via your package manager.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://localhost:8000/docs to browse the API.

## Baseline Docker build: Task 1 starting point

The included `Dockerfile` is intentionally a **single-stage Debian Slim build**. It installs `build-essential`, `gcc`, and `libpq-dev` to compile `psycopg2`, and leaves these packages in the production image. This is the concrete packaging inefficiency to diagnose; don't describe an Alpine failure or missing-library crash unless you observe one.

```bash
docker build --progress=plain -t data-processing-api:baseline .
docker image ls data-processing-api
docker image inspect data-processing-api:baseline --format '{{.Size}}'
docker history data-processing-api:baseline
```

Record the **actual size** of the baseline image. No size or percentage improvement has been pre-measured or guaranteed. If a 30% reduction is not achievable without harming functionality, report the evidence and measured improvement honestly.

### Run local database

```bash
docker compose up -d postgres
```

For the **API in a container**, use `host.docker.internal` for the database host on Docker Desktop (macOS/Windows):

```bash
docker run --rm -d --name sales-api -p 8000:8000 \
  -e DATABASE_URL='postgresql://appuser:localdevpass@host.docker.internal:5432/salesdb' \
  data-processing-api:baseline
```

For the API running directly on your computer, use `localhost` instead. On some Linux Docker installations `host.docker.internal` requires explicit `--add-host=host.docker.internal:host-gateway` or you can use a shared Docker Compose network.

### Validate HTTP endpoints

```bash
curl http://localhost:8000/health
curl http://localhost:8000/db/health
curl -X POST 'http://localhost:8000/sales/summary' \
  -H 'content-type: text/csv' --data-binary @sample_data/sales.csv
curl -X POST 'http://localhost:8000/sales/summary?persist=true' \
  -H 'content-type: text/csv' --data-binary @sample_data/sales.csv
```

Expected `total_revenue` is **570.0**, `completed_orders` is **4**, and `average_order_value` is **142.5**. The persistence call returns a `run_id` if PostgreSQL is reachable.

Clean up with:
```bash
docker stop sales-api
docker compose down
```

## Packaging investigation for your recording

1. Inspect `requirements.txt` and `Dockerfile`: find native dependencies (`psycopg2` and the compiled wheels for NumPy/Pandas).
2. Measure a real **single-stage** baseline via `docker image inspect` and `docker history`.
3. Evaluate Debian `python:3.12-slim-bookworm` against `python:3.12-alpine` for compatible wheels vs. source compilation; record evidence rather than assuming a failure.
4. Choose whether a **two-stage wheel-builder** gives a smaller runtime than the single-stage approach.
5. In a builder stage, install `build-essential` and `libpq-dev`, build/install pinned dependencies; in the final Debian runtime stage, retain **`libpq5`** but omit compilers and dev headers.
6. Keep the final container unprivileged, handle database credentials at runtime, and enhance `.dockerignore`.
7. Validate package consistency via `python -m pip check`; inspect the psycopg2 extension with `ldd` where applicable.
8. Compare sizes against the actual baseline, and verify API, CSV results, and PostgreSQL connectivity.

**Decision limit:** A proposed target of at least 30% smaller is an *objective*, not a proven outcome; validate it with the actual before/after numbers. The tradeoff may favor image correctness over an arbitrary percentage.

## License

MIT; see `LICENSE`. The sample is newly created for this task. Before publishing, set the copyright-holder line to the person or organization that should own and maintain the project, if appropriate.
