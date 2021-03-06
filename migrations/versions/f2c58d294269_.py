"""empty message

Revision ID: f2c58d294269
Revises: cc35d35089f4
Create Date: 2016-01-23 14:29:56.198670

"""

# revision identifiers, used by Alembic.
revision = 'f2c58d294269'
down_revision = 'cc35d35089f4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import sql


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.rename_table('card_transaction', 'old_card_transaction')

    op.alter_column('transaction', 'payment_method',
                    existing_type=sa.Enum(
                        'Battels',
                        'Card',
                        'Free',
                        'Dummy'
                    ),
                    type_=sa.Enum(
                        'Battels',
                        'Card',
                        'OldCard',
                        'Free',
                        'Dummy'
                    ),
                    nullable=False)

    conn = op.get_bind()
    conn.execute(sql.text("""
        UPDATE `transaction`
        SET `payment_method`=:new_payment_method
        WHERE `payment_method`=:old_payment_method
    """), old_payment_method='Card', new_payment_method='OldCard')

    op.create_table('eway_transaction',
    sa.Column('object_id', sa.Integer(), nullable=False),
    sa.Column('access_code', sa.Unicode(length=200), nullable=False),
    sa.Column('charged', sa.Integer(), nullable=False),
    sa.Column('completed', sa.DateTime(), nullable=True),
    sa.Column('result_code', sa.Unicode(length=2), nullable=True),
    sa.Column('eway_id', sa.Integer(), nullable=True),
    sa.Column('refunded', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('object_id')
    )

    op.create_table('card_transaction',
    sa.Column('object_id', sa.Integer(), nullable=False),
    sa.Column('eway_transaction_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['eway_transaction_id'], [u'eway_transaction.object_id'], ),
    sa.ForeignKeyConstraint(['object_id'], [u'transaction.object_id'], ),
    sa.PrimaryKeyConstraint('object_id')
    )

    op.add_column(u'postage', sa.Column('cancelled', sa.Boolean(), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'postage', 'cancelled')

    op.drop_table('new_card_transaction')
    op.drop_table('eway_transaction')

    conn = op.get_bind()
    conn.execute(sql.text("""
        UPDATE `transaction`
        SET `payment_method`=:new_payment_method
        WHERE `payment_method`=:old_payment_method
    """), old_payment_method='OldCard', new_payment_method='Card')

    op.alter_column('transaction', 'payment_method',
                    existing_type=sa.Enum(
                        'Battels',
                        'Card',
                        'OldCard',
                        'Free',
                        'Dummy'
                    ),
                    type_=sa.Enum(
                        'Battels',
                        'Card',
                        'Free',
                        'Dummy'
                    ),
                    nullable=False)

    op.rename_table('old_card_transaction', 'card_transaction')
    ### end Alembic commands ###
