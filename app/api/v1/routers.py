from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.database import get_db
from app.schemas import schemas
from app.db.crud import organization as org_crud



router = APIRouter()


@router.get("/building/{building_id}", 
            response_model=List[schemas.OrganizationOut],
            summary="Список всех организаций находящихся в конкретном здании")
async def get_orgs_by_building(building_id: int, db: AsyncSession = Depends(get_db)):
    return await org_crud.get_by_building(db, building_id)


@router.get("/by-activity", 
            response_model=List[schemas.OrganizationOut],
            summary="Список организаций, относящихся к указанному виду деятельности и всем его подвидам")
async def get_orgs_by_activity(name: str, db: AsyncSession = Depends(get_db)):
    activity = await org_crud.get_activity_by_name(db, name)
    if not activity:
        raise HTTPException(status_code=404, detail="Вид деятельности не найден")
    return await org_crud.get_by_activity_only(db, activity.id)


@router.get("/search-by-name", 
            response_model=List[schemas.OrganizationOut],
            summary="Поиск организации по названию")
async def search_orgs_by_name(name: str, db: AsyncSession = Depends(get_db)):
    return await org_crud.search_by_name(db, name)


@router.get("/geo-search", 
            response_model=List[schemas.OrganizationOut],
            summary="Список организаций, которые находятся в заданном радиусе/прямоугольной области относительно указанной точки на карте. список зданий")
async def geo_search_orgs(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_km: Optional[float] = None,
    lat_min: Optional[float] = None,
    lat_max: Optional[float] = None,
    lon_min: Optional[float] = None,
    lon_max: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    if radius_km and lat is not None and lon is not None:
        return await org_crud.get_by_radius(db, lat, lon, radius_km)
    elif all(v is not None for v in [lat_min, lat_max, lon_min, lon_max]):
        return await org_crud.get_by_rectangle(db, lat_min, lat_max, lon_min, lon_max)
    else:
        raise HTTPException(status_code=400, detail="Укажите либо радиус (lat, lon, radius_km), либо прямоугольник (lat_min, lat_max, lon_min, lon_max)")


@router.get("/search-activity", 
            response_model=List[schemas.OrganizationOut],
            summary="Поиск организаций по виду деятельности (с учётом вложенных подкатегорий)")
async def search_orgs_by_activity_name(name: str, db: AsyncSession = Depends(get_db)):
    activity = await org_crud.get_activity_by_name(db, name)
    if not activity:
        raise HTTPException(status_code=404, detail="Вид деятельности не найден")

    return await org_crud.get_by_activity_tree(db, activity.id)


@router.get("/{org_id}", 
            response_model=schemas.OrganizationOut,
            summary="Вывод информации об организации по её идентификатору")
async def get_org_by_id(org_id: int, db: AsyncSession = Depends(get_db)):
    org = await org_crud.get_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    return org
