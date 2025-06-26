from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from app.models import models
from app.schemas.schemas import OrganizationOut, serialize_activity
from math import radians, cos, sin, asin, sqrt
from typing import List



async def get_by_building(db: AsyncSession, building_id: int) -> List[OrganizationOut]:
    result = await db.execute(
        select(models.Organization)
        .where(models.Organization.building_id == building_id)
        .options(
            selectinload(models.Organization.building),
            selectinload(models.Organization.phones),
            selectinload(models.Organization.activities),
            selectinload(models.Organization.activities, models.OrganizationActivity.activity),
            selectinload(models.Organization.activities, models.OrganizationActivity.activity, models.Activity.children),
        )

    )
    orgs = result.scalars().all()
    return [
        OrganizationOut(
            id=org.id,
            name=org.name,
            building=org.building,
            phones=org.phones,
            activities=[
                serialize_activity(oa.activity, level=1, max_level=3)
                for oa in org.activities
            ]
        )
        for org in orgs
    ]

async def _get_activity_descendants(db: AsyncSession, root_id: int) -> list[int]:
    result = await db.execute(select(models.Activity))
    activities = result.scalars().all()
    descendants = set()
    def collect_children(parent_id: int):
        for activity in activities:
            if activity.parent_id == parent_id:
                descendants.add(activity.id)
                collect_children(activity.id)
    descendants.add(root_id)
    collect_children(root_id)
    return list(descendants)


async def get_by_activity_tree(db: AsyncSession, activity_id: int) -> List[OrganizationOut]:
    activity_ids = await _get_activity_descendants(db, activity_id)
    result = await db.execute(
        select(models.Organization)
        .join(models.OrganizationActivity)
        .where(models.OrganizationActivity.activity_id.in_(activity_ids))
        .options(
            selectinload(models.Organization.building),
            selectinload(models.Organization.phones),
            selectinload(models.Organization.activities)
                .selectinload(models.OrganizationActivity.activity)
                .selectinload(models.Activity.children),
        )
    )
    orgs = result.scalars().unique().all()
    return [
        OrganizationOut(
            id=org.id,
            name=org.name,
            building=org.building,
            phones=org.phones,
            activities=[
                serialize_activity(oa.activity, level=1, max_level=3)
                for oa in org.activities
            ]
        )
        for org in orgs
    ]


async def search_by_name(db: AsyncSession, name: str) -> List[OrganizationOut]:
    result = await db.execute(
        select(models.Organization)
        .where(func.lower(models.Organization.name).like(f"%{name.lower()}%"))
        .options(
            selectinload(models.Organization.building),
            selectinload(models.Organization.phones),
            selectinload(models.Organization.activities)
                .selectinload(models.OrganizationActivity.activity)
                .selectinload(models.Activity.children)
        )
    )
    orgs = result.scalars().all()
    return [
        OrganizationOut(
            id=org.id,
            name=org.name,
            building=org.building,
            phones=org.phones,
            activities=[
                serialize_activity(oa.activity, level=1, max_level=3)
                for oa in org.activities
            ]
        )
        for org in orgs
    ]


async def get_by_id(db: AsyncSession, org_id: int):
    result = await db.execute(
        select(models.Organization)
        .where(models.Organization.id == org_id)
        .options(
            selectinload(models.Organization.building),
            selectinload(models.Organization.phones),
            selectinload(models.Organization.activities).selectinload(models.OrganizationActivity.activity),
        )
    )
    org = result.scalar_one_or_none()
    if org is None:
        return None
    return OrganizationOut(
        id=org.id,
        name=org.name,
        building=org.building,
        phones=org.phones,
        activities=[
            serialize_activity(oa.activity, level=1, max_level=3)
            for oa in org.activities
        ]
    )


def haversine(lat1, lon1, lat2, lon2):
    # Радиус земли в километрах
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


async def get_by_radius(db: AsyncSession, lat: float, lon: float, radius_km: float):
    # все здания
    result = await db.execute(select(models.Building))
    buildings = result.scalars().all()
    # фильтр по радиусу
    nearby_ids = [
        b.id for b in buildings if haversine(lat, lon, b.latitude, b.longitude) <= radius_km
    ]
    if not nearby_ids:
        return []
    # организации из найденных зданий
    result = await db.execute(
        select(models.Organization)
        .where(models.Organization.building_id.in_(nearby_ids))
        .options(
            selectinload(models.Organization.building),
            selectinload(models.Organization.phones),
            selectinload(models.Organization.activities).selectinload(models.OrganizationActivity.activity),
        )
    )
    orgs = result.scalars().all()
    return [
        OrganizationOut(
            id=org.id,
            name=org.name,
            building=org.building,
            phones=org.phones,
            activities=[
                serialize_activity(oa.activity, level=1, max_level=3)
                for oa in org.activities
            ]
        )
        for org in orgs
    ]


async def get_by_rectangle(db: AsyncSession, lat_min: float, lat_max: float, lon_min: float, lon_max: float):
    # получение здания внутри прямоугольника
    result = await db.execute(
        select(models.Building).where(
            models.Building.latitude >= lat_min,
            models.Building.latitude <= lat_max,
            models.Building.longitude >= lon_min,
            models.Building.longitude <= lon_max,
        )
    )
    buildings = result.scalars().all()
    if not buildings:
        return []
    building_ids = [b.id for b in buildings]
    result = await db.execute(
        select(models.Organization)
        .where(models.Organization.building_id.in_(building_ids))
        .options(
            selectinload(models.Organization.building),
            selectinload(models.Organization.phones),
            selectinload(models.Organization.activities).selectinload(models.OrganizationActivity.activity),
        )
    )
    orgs = result.scalars().all()
    return [
        OrganizationOut(
            id=org.id,
            name=org.name,
            building=org.building,
            phones=org.phones,
            activities=[
                serialize_activity(oa.activity, level=1, max_level=3)
                for oa in org.activities
            ]
        )
        for org in orgs
    ]


async def get_activity_by_name(db: AsyncSession, name: str):
    result = await db.execute(
        select(models.Activity).where(func.lower(models.Activity.name) == name.lower())
    )
    return result.scalar_one_or_none()


async def get_by_activity_only(db: AsyncSession, activity_id: int) -> List[OrganizationOut]:
    result = await db.execute(
        select(models.Organization)
        .join(models.Organization.activities)
        .where(models.OrganizationActivity.activity_id == activity_id)
        .options(
            selectinload(models.Organization.building),
            selectinload(models.Organization.phones),
            selectinload(models.Organization.activities)
            .selectinload(models.OrganizationActivity.activity)
            .selectinload(models.Activity.children)
        )
    )
    orgs = result.scalars().all()
    return [
        OrganizationOut(
            id=org.id,
            name=org.name,
            building=org.building,
            phones=org.phones,
            activities=[
                serialize_activity(oa.activity, level=1, max_level=3)
                for oa in org.activities
            ]
        )
        for org in orgs
    ]