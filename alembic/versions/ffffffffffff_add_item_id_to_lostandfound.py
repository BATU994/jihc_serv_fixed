"""
add item_id to lostandfound

Revision ID: ffffffffffff
Revises:  c8fb3fdaeec5
Create Date: 2025-09-29
"""

from alembic import op
import sqlalchemy as sa
from uuid import uuid4

# revision identifiers, used by Alembic.
revision = 'ffffffffffff'
down_revision = 'c8fb3fdaeec5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('lostandfound', sa.Column('item_id', sa.Text(), nullable=True))
    # Backfill unique ids
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM lostandfound WHERE item_id IS NULL"))
    ids = [row[0] for row in result]
    for row_id in ids:
        conn.execute(sa.text("UPDATE lostandfound SET item_id=:iid WHERE id=:id"), {"iid": uuid4().hex, "id": row_id})
    op.alter_column('lostandfound', 'item_id', nullable=False)
    op.create_unique_constraint('uq_lostandfound_item_id', 'lostandfound', ['item_id'])


def downgrade() -> None:
    op.drop_constraint('uq_lostandfound_item_id', 'lostandfound', type_='unique')
    op.drop_column('lostandfound', 'item_id')


