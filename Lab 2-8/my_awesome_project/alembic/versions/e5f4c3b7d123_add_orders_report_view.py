"""Add orders report view

Revision ID: e5f4c3b7d123
Revises: d3a6fece16d8
Create Date: 2025-12-16 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5f4c3b7d123"
down_revision: Union[str, Sequence[str], None] = "d3a6fece16d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create SQL view `report_orders`.

    The view has these columns:
    - report_at: date (day of order created_at)
    - order_id: uuid of the order
    - count_product: total count of products in the order (sum of quantities)
    """
    op.execute(
        """
        CREATE OR REPLACE VIEW report_orders AS
        SELECT
            DATE(o.created_at) AS report_at,
            o.id AS order_id,
            COALESCE(SUM(oi.quantity), 0) AS count_product
        FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.id
        GROUP BY DATE(o.created_at), o.id
        """
    )


def downgrade() -> None:
    """Drop the `report_orders` view."""
    op.execute("DROP VIEW IF EXISTS report_orders")
