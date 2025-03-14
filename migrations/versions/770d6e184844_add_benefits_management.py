"""add_benefits_management

Revision ID: 770d6e184844
Revises: 5ff7ad786655
Create Date: 2025-03-04 22:29:29.892968

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '770d6e184844'
down_revision = '5ff7ad786655'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('benefits',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_benefits_id'), 'benefits', ['id'], unique=False)
    op.create_table('employee_benefits',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('benefit_id', sa.String(length=36), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['benefit_id'], ['benefits.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_benefits_id'), 'employee_benefits', ['id'], unique=False)
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_employee_benefits_id'), table_name='employee_benefits')
    op.drop_table('employee_benefits')
    op.drop_index(op.f('ix_benefits_id'), table_name='benefits')
    op.drop_table('benefits')
    # ### end Alembic commands ###