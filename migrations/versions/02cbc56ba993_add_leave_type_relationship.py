"""add_leave_type_relationship

Revision ID: 02cbc56ba993
Revises: 2bd9eed78d1f
Create Date: 2025-03-04 20:44:07.421275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '02cbc56ba993'
down_revision = '2bd9eed78d1f'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('leaves', 'leave_type')
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('leaves', sa.Column('leave_type', sa.VARCHAR(length=50, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False))
    # ### end Alembic commands ###