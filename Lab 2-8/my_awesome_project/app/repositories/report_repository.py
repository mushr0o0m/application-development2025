from __future__ import annotations

from datetime import date
from typing import Any

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class ReportRepository:
    """Reads aggregated order data from the report view."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_by_date(self, report_date: date) -> list[dict[str, Any]]:
        """Return rows for the given report date."""

        stmt = text(
            """
            SELECT report_at, order_id, count_product
            FROM report_orders
            WHERE report_at = :report_date
            ORDER BY order_id
            """
        )
        try:
            result = await self.db.execute(stmt, {"report_date": report_date})
        except Exception as exc:  # defensive: DB unavailable, auth error, etc.
            logging.exception("Failed to execute report query for date %s", report_date)
            # Do not swallow the error: re-raise so caller gets the real exception.
            raise

        rows: list[dict[str, Any]] = []
        for row in result:
            rows.append(
                {
                    "report_at": row.report_at,
                    "order_id": row.order_id,
                    "count_product": int(row.count_product or 0),
                }
            )
        return rows

