"""empty message

Revision ID: 5ce00ca1cea8
Revises: aba0a6b0bfa2
Create Date: 2016-02-10 17:41:30.054245

"""

# revision identifiers, used by Alembic.
revision = '5ce00ca1cea8'
down_revision = 'aba0a6b0bfa2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import sql


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dietary_requirements',
    sa.Column('object_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('pescetarian', sa.Boolean(), nullable=False),
    sa.Column('vegetarian', sa.Boolean(), nullable=False),
    sa.Column('vegan', sa.Boolean(), nullable=False),
    sa.Column('gluten_free', sa.Boolean(), nullable=False),
    sa.Column('nut_free', sa.Boolean(), nullable=False),
    sa.Column('dairy_free', sa.Boolean(), nullable=False),
    sa.Column('egg_free', sa.Boolean(), nullable=False),
    sa.Column('seafood_free', sa.Boolean(), nullable=False),
    sa.Column('other', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], [u'user.object_id'], ),
    sa.PrimaryKeyConstraint('object_id')
    )

    op.alter_column(
        'statistic',
        'group',
        existing_type=sa.Enum(
            'college_users',
            'payment_methods',
            'ticket_types',
            'total_ticket_sales',
            'guest_ticket_sales',
            'waiting',
        ),
        type_=sa.Enum(
            'college_users',
            'payment_methods',
            'ticket_types',
            'total_ticket_sales',
            'guest_ticket_sales',
            'waiting',
            'dietary_requirements',
        ),
        nullable=False
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()

    conn.execute(sql.text("""
        DELETE FROM `statistic`
        WHERE `group`=:group
    """), group='dietary_requirements')

    op.alter_column(
        'statistic',
        'group',
        existing_type=sa.Enum(
            'college_users',
            'payment_methods',
            'ticket_types',
            'total_ticket_sales',
            'guest_ticket_sales',
            'waiting',
            'dietary_requirements',
        ),
        type_=sa.Enum(
            'college_users',
            'payment_methods',
            'ticket_types',
            'total_ticket_sales',
            'guest_ticket_sales',
            'waiting',
        ),
        nullable=False
    )

    op.drop_table('dietary_requirements')
    ### end Alembic commands ###
