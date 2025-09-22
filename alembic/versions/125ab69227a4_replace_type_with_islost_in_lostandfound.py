"""replace type with isLost in lostandfound

Revision ID: 125ab69227a4
Revises: a237a0890b62
Create Date: 2025-09-22 16:04:00.386174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '125ab69227a4'
down_revision = 'a237a0890b62'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use batch operations for SQLite compatibility
    with op.batch_alter_table('lostandfound', schema=None) as batch_op:
        batch_op.alter_column('image',
            existing_type=sa.BLOB(),
            type_=sa.Text(),
            existing_nullable=True)


def downgrade() -> None:
    # Use batch operations for SQLite compatibility
    with op.batch_alter_table('lostandfound', schema=None) as batch_op:
        batch_op.alter_column('image',
            existing_type=sa.Text(),
            type_=sa.BLOB(),
            existing_nullable=True)