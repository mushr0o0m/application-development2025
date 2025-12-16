from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class ReportRow(BaseModel):
    report_at: date
    order_id: UUID
    count_product: int = Field(ge=0)

    model_config = {"from_attributes": True}


class ReportResponse(BaseModel):
    report_date: date
    items: list[ReportRow] = Field(default_factory=list)
    total: int

