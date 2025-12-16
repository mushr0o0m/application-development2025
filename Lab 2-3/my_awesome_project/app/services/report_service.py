from __future__ import annotations

from datetime import date

from app.repositories.report_repository import ReportRepository


class ReportService:
    """High-level access to report view data."""

    def __init__(self, report_repository: ReportRepository):
        self.report_repository = report_repository

    async def get_for_date(self, report_date: date):
        return await self.report_repository.fetch_by_date(report_date)

