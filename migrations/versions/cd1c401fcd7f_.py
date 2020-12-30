"""empty message

Revision ID: cd1c401fcd7f
Revises: 
Create Date: 2020-12-07 23:53:29.359362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd1c401fcd7f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('h_area_info',
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('h_facility_info',
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('h_user_profile',
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('mobile', sa.String(length=11), nullable=False),
    sa.Column('real_name', sa.String(length=32), nullable=True),
    sa.Column('id_card', sa.String(length=20), nullable=True),
    sa.Column('avatar_url', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('mobile'),
    sa.UniqueConstraint('name')
    )
    op.create_table('h_house_info',
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('area_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=64), nullable=False),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('address', sa.String(length=512), nullable=True),
    sa.Column('room_count', sa.Integer(), nullable=True),
    sa.Column('acreage', sa.Integer(), nullable=True),
    sa.Column('unit', sa.String(length=32), nullable=True),
    sa.Column('capacity', sa.Integer(), nullable=True),
    sa.Column('beds', sa.String(length=64), nullable=True),
    sa.Column('deposit', sa.Integer(), nullable=True),
    sa.Column('min_days', sa.Integer(), nullable=True),
    sa.Column('max_days', sa.Integer(), nullable=True),
    sa.Column('order_count', sa.Integer(), nullable=True),
    sa.Column('index_image_url', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['area_id'], ['h_area_info.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['h_user_profile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('h_house_facility',
    sa.Column('house_id', sa.Integer(), nullable=False),
    sa.Column('facility_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['facility_id'], ['h_facility_info.id'], ),
    sa.ForeignKeyConstraint(['house_id'], ['h_house_info.id'], ),
    sa.PrimaryKeyConstraint('house_id', 'facility_id')
    )
    op.create_table('h_house_image',
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('house_id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(length=256), nullable=False),
    sa.ForeignKeyConstraint(['house_id'], ['h_house_info.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('h_order_info',
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('house_id', sa.Integer(), nullable=False),
    sa.Column('begin_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('days', sa.Integer(), nullable=False),
    sa.Column('house_price', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('WAIT_ACCEPT', 'WAIT_PAYMENT', 'PAID', 'WAIT_COMMENT', 'COMPLETE', 'CANCELED', 'REJECTED'), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('trade_no', sa.String(length=80), nullable=True),
    sa.ForeignKeyConstraint(['house_id'], ['h_house_info.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['h_user_profile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_h_order_info_status'), 'h_order_info', ['status'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_h_order_info_status'), table_name='h_order_info')
    op.drop_table('h_order_info')
    op.drop_table('h_house_image')
    op.drop_table('h_house_facility')
    op.drop_table('h_house_info')
    op.drop_table('h_user_profile')
    op.drop_table('h_facility_info')
    op.drop_table('h_area_info')
    # ### end Alembic commands ###
