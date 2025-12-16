from __future__ import annotations

from datetime import date

from litestar import Controller, get
from litestar.exceptions import HTTPException
from litestar.params import Parameter

from app.schemas import ReportResponse, ReportRow
from app.services.report_service import ReportService


class ReportController(Controller):
    path = "/report"

    @get()
    async def get_report(
        self,
        report_service: ReportService,
        report_date: date = Parameter(
            default=...,  # required query parameter
            description="Target date in YYYY-MM-DD format",
        ),
    ) -> ReportResponse:
        try:
            rows = await report_service.get_for_date(report_date)
        except Exception as exc:  # pragma: no cover - defensive path
            raise HTTPException(
                status_code=500,
                detail="Report view is not available",
            ) from exc

        # Normalize rows to plain python types before validation. SQLAlchemy rows
        # may contain datetime/UUID objects or be row-proxy objects.
        items: list[ReportRow] = []
        for row in rows:
            data = dict(row) if not isinstance(row, dict) else row
            report_at = data.get("report_at")
            # If report_at is a datetime, convert to date
            if hasattr(report_at, "date"):
                report_at = report_at.date()
            items.append(
                ReportRow.model_validate(
                    {
                        "report_at": report_at,
                        "order_id": str(data.get("order_id")),
                        "count_product": int(data.get("count_product") or 0),
                    }
                )
            )

        return ReportResponse(report_date=report_date, items=items, total=len(items))

