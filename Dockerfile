# BASELINE ONLY: single-stage build intentionally retains compile-time packages.
# Your Task 1 recording should inspect and optimize this file.
FROM python:3.12-slim-bookworm

WORKDIR /service

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY sample_data ./sample_data

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
