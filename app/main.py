"""FastAPI service for sales CSV analytics and optional PostgreSQL persistence."""
from fastapi import FastAPI, HTTPException, Query, Request

from app.database import check_database, save_summary
from app.processor import SalesValidationError, summarize_sales

app = FastAPI(title="Data Processing API", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "data-processing-api"}


@app.get("/db/health")
def database_health():
    try:
        check_database()
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database check failed: {type(exc).__name__}") from exc


@app.post("/sales/summary")
async def sales_summary(request: Request, persist: bool = Query(False)):
    body = (await request.body()).decode("utf-8", errors="replace")
    try:
        result = summarize_sales(body)
    except SalesValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if persist:
        try:
            result["run_id"] = save_summary(result)
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Persistence failed: {type(exc).__name__}") from exc
    return result
