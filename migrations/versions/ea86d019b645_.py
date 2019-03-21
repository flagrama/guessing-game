"""empty message

Revision ID: ea86d019b645
Revises: 468a1d683c21
Create Date: 2019-03-18 18:33:17.359815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea86d019b645'
down_revision = '468a1d683c21'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('bot_enabled', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###
    new_column = sa.table('users', sa.column('bot_enabled'))
    op.execute(new_column.update().values(**{'bot_enabled': False}))
    op.alter_column('users', 'bot_enabled', nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'bot_enabled')
    # ### end Alembic commands ###