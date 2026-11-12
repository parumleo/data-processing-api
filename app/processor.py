"""CSV validation and sales aggregation; no database needed for this stage."""
from io import StringIO

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {"order_id", "order_date", "region", "category", "quantity", "unit_price", "status"}


class SalesValidationError(ValueError):
    """Raised when a CSV cannot be processed safely."""


def summarize_sales(csv_text: str) -> dict:
    if not csv_text.strip():
        raise SalesValidationError("CSV body cannot be empty")
    try:
        df = pd.read_csv(StringIO(csv_text))
    except Exception as exc:
        raise SalesValidationError("Malformed CSV") from exc
    missing = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing:
        raise SalesValidationError(f"Missing columns: {', '.join(missing)}")
    if df.empty:
        raise SalesValidationError("CSV must contain at least one data row")
    if df["order_id"].isna().any() or df["order_id"].duplicated().any():
        raise SalesValidationError("order_id must be present and unique")
    try:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="raise")
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="raise")
        dates = pd.to_datetime(df["order_date"], format="%Y-%m-%d", errors="raise")
    except (ValueError, TypeError) as exc:
        raise SalesValidationError("Invalid quantity, unit_price, or order_date") from exc
    if df[["quantity", "unit_price"]].isna().any().any() or not np.isfinite(df[["quantity", "unit_price"]].to_numpy(dtype=float)).all():
        raise SalesValidationError("quantity and unit_price must be finite numbers")
    if (df["quantity"] <= 0).any() or (df["unit_price"] < 0).any():
        raise SalesValidationError("quantity must be positive and unit_price must be nonnegative")
    if (dates.isna()).any():
        raise SalesValidationError("Invalid order_date")
    if df["region"].isna().any() or df["category"].isna().any():
        raise SalesValidationError("region and category are required")
    completed = df[df["status"].astype(str).str.lower().str.strip() == "completed"].copy()
    completed["revenue"] = completed["quantity"] * completed["unit_price"]
    grouped = completed.groupby("region", dropna=False)["revenue"].sum().sort_index()
    total = float(np.round(completed["revenue"].sum(), 2))
    return {
        "received_orders": int(len(df)),
        "completed_orders": int(len(completed)),
        "total_revenue": round(total, 2),
        "average_order_value": round(total / len(completed), 2) if len(completed) else 0.0,
        "revenue_by_region": {str(k): round(float(v), 2) for k, v in grouped.items()},
    }
