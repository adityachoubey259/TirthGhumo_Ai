"""add case-insensitive tour package duplicate protection

Revision ID: 20261006_0001
Revises: a002bce61e9a
Create Date: 2026-10-06

"""
from typing import Sequence, Union

from alembic import op


revision: str = "20261006_0001"
down_revision: Union[str, Sequence[str], None] = "a002bce61e9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNIQUE INDEX uq_tour_packages_name_destination_ci
        ON tour_packages (lower(name), lower(destination))
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_tour_packages_name_destination_ci")
