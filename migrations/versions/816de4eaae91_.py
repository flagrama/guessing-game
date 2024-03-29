"""empty message

Revision ID: 816de4eaae91
Revises: 69aaa8c3fcbe
Create Date: 2019-03-29 19:05:48.474599

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '816de4eaae91'
down_revision = '69aaa8c3fcbe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('results',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('datetime', sa.DateTime(), nullable=True),
    sa.Column('results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('results')
    # ### end Alembic commands ###
