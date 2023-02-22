"""empty message

Revision ID: e05ca5cdc312
Revises: ca9b79dde5cc
Create Date: 2023-02-08 12:21:41.722774

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e05ca5cdc312'
down_revision = 'ca9b79dde5cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('spiff_step_details', sa.Column('task_state', sa.String(length=50), nullable=False))
    op.add_column('spiff_step_details', sa.Column('task_id', sa.String(length=50), nullable=False))
    op.add_column('spiff_step_details', sa.Column('bpmn_task_identifier', sa.String(length=255), nullable=False))
    op.add_column('spiff_step_details', sa.Column('engine_step_start_in_seconds', sa.DECIMAL(precision=17, scale=6), nullable=True))
    op.add_column('spiff_step_details', sa.Column('engine_step_end_in_seconds', sa.DECIMAL(precision=17, scale=6), nullable=True))
    op.drop_column('spiff_step_details', 'timestamp')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('spiff_step_details', sa.Column('timestamp', mysql.DECIMAL(precision=17, scale=6), nullable=False))
    op.drop_column('spiff_step_details', 'engine_step_end_in_seconds')
    op.drop_column('spiff_step_details', 'engine_step_start_in_seconds')
    op.drop_column('spiff_step_details', 'bpmn_task_identifier')
    op.drop_column('spiff_step_details', 'task_id')
    op.drop_column('spiff_step_details', 'task_state')
    # ### end Alembic commands ###