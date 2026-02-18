import pandas as pd
import math
def _clean_number(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return x

    if math.isnan(x) or math.isinf(x):
        return None
    return x

def _sanitize(obj):
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, (int, str, bool)) or obj is None:
        return obj
    if isinstance(obj, float):
        return _clean_number(obj)
    return _clean_number(obj)

def _series_to_json_dict(s):
    if s is None:
        return None
    d = s.to_dict()  
    return {str(k): float(v) for k, v in d.items()}
def make_json_safe(results: dict) -> dict:
    safe = {}

    cashflow = results.get("cashflow") or {}
    time = results.get("time") or {}
    category = results.get("category") or {}
    outlier = results.get("outliers") or {}
    top_merchants = results.get("top_merchants")

    safe["category"] = {
        "total_by_category": category["total_by_category"].to_dict()
        if category.get("total_by_category") is not None else None,

        "avg_by_category": category["avg_by_category"].to_dict()
        if category.get("avg_by_category") is not None else None,

        "count_by_category": category["count_by_category"].to_dict()
        if category.get("count_by_category") is not None else None,

        "percent_by_category": category["percent_by_category"].to_dict()
        if category.get("percent_by_category") is not None else None,

        "high_share_categories": category["high_share_categories"].to_dict()
        if category.get("high_share_categories") is not None else None,

        "top_spending_category": category.get("top_spending_category"),
        "top_spending_value": float(category["top_spending_value"])
        if category.get("top_spending_value") is not None else None,
    }

    safe["time"] = {
        "total_by_month": _series_to_json_dict(time.get("total_by_month")),
        "highest_month": str(time["highest_month"]) if time.get("highest_month") is not None else None,
        "highest_month_value": float(time["highest_month_value"]) if time.get("highest_month_value") is not None else None,
        "has_trend": bool(time.get("has_trend", False)),
        "month_over_month_change": _series_to_json_dict(time.get("month_over_month_change")),
    }

    large_df = outlier.get("large_transactions")
    if large_df is None or getattr(large_df, "empty", True):
        large_json = []
    else:
        large_df = large_df.copy()
        if "month" in large_df.columns:
            large_df["month"] = large_df["month"].astype(str)
        if "date" in large_df.columns:
            large_df["date"] = large_df["date"].astype(str)
        large_json = large_df.to_dict(orient="records")

    safe["outliers"] = {
        "mean_amount": float(outlier.get("mean_amount", 0)),
        "large_transactions": large_json,
        "num_large_transactions": int(outlier.get("num_large_transactions", 0)),
    }

    safe["cashflow"] = {
        "income_by_month": _series_to_json_dict(cashflow.get("income_by_month")),
        "expenses_by_month": _series_to_json_dict(cashflow.get("expenses_by_month")),
        "net_savings_by_month": _series_to_json_dict(cashflow.get("net_savings_by_month")),
        "total_net_savings": float(cashflow.get("total_net_savings", 0)),
        "expectation": float(cashflow.get("expectation", 0) or 0)
    }

    safe["top_merchants"] = (
        top_merchants.to_dict() if top_merchants is not None else None
    )

    return _sanitize(safe)