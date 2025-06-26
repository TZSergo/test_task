"""add_test_data

Revision ID: 91cb07320987
Revises: 8155d133fe3a
Create Date: 2025-06-25 19:12:08.045592

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Float


# revision identifiers, used by Alembic.
revision: str = '91cb07320987'
down_revision: Union[str, Sequence[str], None] = '8155d133fe3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    activities = table(
        'activities',
        column('id', Integer),
        column('name', String),
        column('parent_id', Integer),
    )

    buildings = table(
        'buildings',
        column('id', Integer),
        column('address', String),
        column('latitude', Float),
        column('longitude', Float),
    )

    organizations = table(
        'organizations',
        column('id', Integer),
        column('name', String),
        column('building_id', Integer),
    )

    organization_phones = table(
        'organization_phones',
        column('id', Integer),
        column('organization_id', Integer),
        column('phone_number', String),
    )

    organization_activities = table(
        'organization_activities',
        column('id', Integer),
        column('organization_id', Integer),
        column('activity_id', Integer),
    )

    op.bulk_insert(activities, [
        {"id": 1, "name": "Еда", "parent_id": None},
        {"id": 2, "name": "Молочная продукция", "parent_id": 1},
        {"id": 3, "name": "Мясная продукция", "parent_id": 1},
        {"id": 4, "name": "Автомобили", "parent_id": None},
        {"id": 5, "name": "Грузовые", "parent_id": 4},
    ])

    op.bulk_insert(buildings, [
        {"id": 1, "address": "г. Москва, ул. Ленина 1", "latitude": 55.7558, "longitude": 37.6173},
        {"id": 2, "address": "г. Москва, ул. Тверская 10", "latitude": 55.7658, "longitude": 37.6256},
    ])

    op.bulk_insert(organizations, [
        {"id": 1, "name": "ООО Рога и Копыта", "building_id": 1},
        {"id": 2, "name": "ЗАО Молоко", "building_id": 1},
        {"id": 3, "name": "ИП Мясной Дом", "building_id": 2},
    ])

    op.bulk_insert(organization_phones, [
        {"id": 1, "organization_id": 1, "phone_number": "2-222-222"},
        {"id": 2, "organization_id": 1, "phone_number": "3-333-333"},
        {"id": 3, "organization_id": 2, "phone_number": "8-800-555-35-35"},
        {"id": 4, "organization_id": 3, "phone_number": "8-923-666-13-13"},
    ])

    op.bulk_insert(organization_activities, [
        {"id": 1, "organization_id": 1, "activity_id": 3},
        {"id": 2, "organization_id": 2, "activity_id": 2},
        {"id": 3, "organization_id": 3, "activity_id": 3},
    ])


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM organization_activities")
    op.execute("DELETE FROM organization_phones")
    op.execute("DELETE FROM organizations")
    op.execute("DELETE FROM buildings")
    op.execute("DELETE FROM activities")
