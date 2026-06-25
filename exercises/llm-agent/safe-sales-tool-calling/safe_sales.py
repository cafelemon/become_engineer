from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any


TOOL_NAME = "get_monthly_sales"
MAX_RESULT_ROWS = 50

TOOL_SCHEMA = {
    "type": "function",
    "name": TOOL_NAME,
    "description": "Query a monthly sales summary, optionally filtered by product name.",
    "parameters": {
        "type": "object",
        "properties": {
            "year": {
                "type": "integer",
                "description": "Four-digit calendar year from 2000 through 2100.",
            },
            "month": {
                "type": "integer",
                "minimum": 1,
                "maximum": 12,
            },
            "product_name": {
                "type": ["string", "null"],
                "description": "Exact product name, or null for all products.",
            },
        },
        "required": ["year", "month", "product_name"],
        "additionalProperties": False,
    },
    "strict": True,
}


class ToolValidationError(ValueError):
    """Raised when a model-proposed tool call is not safe to execute."""


def initialize_demo_database(
    db_path: Path,
    *,
    seed_path: Path | None = None,
    overwrite: bool = False,
) -> Path:
    db_path = Path(db_path)
    if db_path.exists() and not overwrite:
        return db_path

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    seed_path = seed_path or Path(__file__).parent / "data" / "seed.sql"
    seed_sql = Path(seed_path).read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as connection:
        connection.executescript(seed_sql)
    return db_path


def connect_read_only(db_path: Path) -> sqlite3.Connection:
    db_path = Path(db_path).resolve()
    if not db_path.is_file():
        raise FileNotFoundError(f"Database does not exist: {db_path}")

    connection = sqlite3.connect(f"{db_path.as_uri()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _validate_year_month(year: Any, month: Any) -> tuple[int, int]:
    if type(year) is not int or not 2000 <= year <= 2100:
        raise ToolValidationError("year must be an integer from 2000 through 2100")
    if type(month) is not int or not 1 <= month <= 12:
        raise ToolValidationError("month must be an integer from 1 through 12")
    return year, month


def _validate_product_name(product_name: Any) -> str | None:
    if product_name is None:
        return None
    if not isinstance(product_name, str):
        raise ToolValidationError("product_name must be a string or null")

    product_name = product_name.strip()
    if not product_name:
        raise ToolValidationError("product_name cannot be blank")
    if len(product_name) > 80:
        raise ToolValidationError("product_name cannot exceed 80 characters")
    if any(ord(character) < 32 for character in product_name):
        raise ToolValidationError("product_name cannot contain control characters")
    return product_name


def _next_month(year: int, month: int) -> date:
    if month == 12:
        return date(year + 1, 1, 1)
    return date(year, month + 1, 1)


def get_monthly_sales(
    db_path: Path,
    *,
    year: int,
    month: int,
    product_name: str | None,
) -> dict[str, Any]:
    year, month = _validate_year_month(year, month)
    product_name = _validate_product_name(product_name)

    start = date(year, month, 1)
    end = _next_month(year, month)
    query = """
        SELECT
            product_name,
            SUM(quantity) AS units,
            SUM(quantity * unit_price_cents) AS revenue_cents
        FROM sales
        WHERE sold_at >= ? AND sold_at < ?
    """
    parameters: list[Any] = [start.isoformat(), end.isoformat()]

    if product_name is not None:
        query += " AND product_name = ?"
        parameters.append(product_name)

    query += """
        GROUP BY product_name
        ORDER BY revenue_cents DESC, product_name ASC
        LIMIT ?
    """
    parameters.append(MAX_RESULT_ROWS)

    with connect_read_only(db_path) as connection:
        rows = connection.execute(query, parameters).fetchall()

    items = [
        {
            "product_name": row["product_name"],
            "units": row["units"],
            "revenue_cents": row["revenue_cents"],
        }
        for row in rows
    ]
    return {
        "ok": True,
        "year": year,
        "month": month,
        "product_name": product_name,
        "currency": "CNY",
        "items": items,
        "total_units": sum(item["units"] for item in items),
        "total_revenue_cents": sum(item["revenue_cents"] for item in items),
    }


def execute_tool_call(
    db_path: Path,
    *,
    name: str,
    arguments: str | dict[str, Any],
) -> dict[str, Any]:
    if name != TOOL_NAME:
        raise ToolValidationError(f"unknown tool: {name}")

    if isinstance(arguments, str):
        try:
            parsed_arguments = json.loads(arguments)
        except json.JSONDecodeError as error:
            raise ToolValidationError("arguments must be valid JSON") from error
    elif isinstance(arguments, dict):
        parsed_arguments = dict(arguments)
    else:
        raise ToolValidationError("arguments must be a JSON object")

    expected_keys = {"year", "month", "product_name"}
    extra_keys = set(parsed_arguments) - expected_keys
    missing_keys = expected_keys - set(parsed_arguments)
    if extra_keys:
        raise ToolValidationError(
            f"unexpected argument fields: {', '.join(sorted(extra_keys))}"
        )
    if missing_keys:
        raise ToolValidationError(
            f"missing argument fields: {', '.join(sorted(missing_keys))}"
        )

    return get_monthly_sales(db_path, **parsed_arguments)


def run_offline_tool_call(
    db_path: Path,
    *,
    year: int,
    month: int,
    product_name: str | None,
) -> dict[str, Any]:
    function_call = {
        "type": "function_call",
        "call_id": "offline-call-1",
        "name": TOOL_NAME,
        "arguments": json.dumps(
            {
                "year": year,
                "month": month,
                "product_name": product_name,
            },
            ensure_ascii=False,
        ),
    }
    result = execute_tool_call(
        db_path,
        name=function_call["name"],
        arguments=function_call["arguments"],
    )
    function_call_output = {
        "type": "function_call_output",
        "call_id": function_call["call_id"],
        "output": json.dumps(result, ensure_ascii=False),
    }
    return {
        "function_call": function_call,
        "function_call_output": function_call_output,
        "result": result,
    }
