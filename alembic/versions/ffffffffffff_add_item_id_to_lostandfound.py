"""
add item_id to lostandfound

Revision ID: ffffffffffff
Revises: c8fb3fdaeec5
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
    conn = op.get_bind()
    # Check if column already exists (idempotent for SQLite)
    cols = conn.execute(sa.text("PRAGMA table_info(lostandfound)")).fetchall()
    col_names = {row[1] for row in cols}  # second column is name
    if 'item_id' not in col_names:
        op.add_column('lostandfound', sa.Column('item_id', sa.Text(), nullable=True))
    # Backfill any missing item_id values
    result = conn.execute(sa.text("SELECT id FROM lostandfound WHERE item_id IS NULL OR item_id = ''"))
    ids = [row[0] for row in result]
    for row_id in ids:
        conn.execute(sa.text("UPDATE lostandfound SET item_id=:iid WHERE id=:id"), {"iid": uuid4().hex, "id": row_id})
    # Create a unique index on item_id (works in SQLite)
    op.create_index('uq_lostandfound_item_id', 'lostandfound', ['item_id'], unique=True)


def downgrade() -> None:
    op.drop_index('uq_lostandfound_item_id', table_name='lostandfound')
    # Drop column only if exists; SQLite can't drop columns before 3.35, but Alembic will no-op if unsupported
    with op.batch_alter_table('lostandfound') as batch_op:
        try:
            batch_op.drop_column('item_id')
        except Exception:
            pass


