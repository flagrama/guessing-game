"""empty message

Revision ID: 35f349692ebe
Revises: 816de4eaae91
Create Date: 2019-04-04 00:29:01.264578

"""
import json
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '35f349692ebe'
down_revision = '816de4eaae91'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('whitelist', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    # ### end Alembic commands ###
    new_column = sa.table('users', sa.column('whitelist'))
    op.execute(new_column.update().values(**{'whitelist': json.dumps([])}))
    op.alter_column('users', 'whitelist', nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'whitelist')
    # ### end Alembic commands ###