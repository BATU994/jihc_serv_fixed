"""
add user_uuid to users

Revision ID: eeeeeeeeeeee
Revises: ffffffffffff
Create Date: 2025-09-29
"""

from alembic import op
import sqlalchemy as sa
from uuid import uuid4

revision = 'eeeeeeeeeeee'
down_revision = 'ffffffffffff'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    # add column if missing
    cols = conn.execute(sa.text("PRAGMA table_info(users)")).fetchall()
    names = {row[1] for row in cols}
    if 'user_uuid' not in names:
        op.add_column('users', sa.Column('user_uuid', sa.Text(), nullable=True))
    # backfill nulls
    result = conn.execute(sa.text("SELECT id FROM users WHERE user_uuid IS NULL OR user_uuid = ''"))
    ids = [row[0] for row in result]
    for row_id in ids:
        conn.execute(sa.text("UPDATE users SET user_uuid=:u WHERE id=:id"), {"u": uuid4().hex, "id": row_id})
    # create unique index
    op.create_index('uq_users_user_uuid', 'users', ['user_uuid'], unique=True)


def downgrade() -> None:
    op.drop_index('uq_users_user_uuid', table_name='users')
    with op.batch_alter_table('users') as batch_op:
        try:
            batch_op.drop_column('user_uuid')
        except Exception:
            pass


