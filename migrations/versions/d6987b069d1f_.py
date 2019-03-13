"""empty message

Revision ID: d6987b069d1f
Revises: 
Create Date: 2019-03-13 14:17:47.308728

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6987b069d1f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('twitch_id', sa.Integer(), nullable=True),
    sa.Column('twitch_login_name', sa.String(), nullable=True),
    sa.Column('twitch_display_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
