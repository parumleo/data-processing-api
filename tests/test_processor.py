from pathlib import Path

import pytest
from app.processor import SalesValidationError, summarize_sales

EXAMPLE = (Path(__file__).resolve().parents[1] / "sample_data" / "sales.csv").read_text()


def test_csv_sales_aggregation():
    result = summarize_sales(EXAMPLE)
    assert result == {
        "received_orders": 6,
        "completed_orders": 4,
        "total_revenue": 570.0,
        "average_order_value": 142.5,
        "revenue_by_region": {"East": 120.0, "North": 200.0, "South": 250.0},
    }


def test_missing_columns_rejected():
    with pytest.raises(SalesValidationError, match="Missing columns"):
        summarize_sales("order_id,quantity\n1,1")


def test_duplicate_order_rejected():
    with pytest.raises(SalesValidationError, match="unique"):
        summarize_sales(EXAMPLE + "101,2026-01-01,North,Hardware,1,10,Completed\n")
