from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.models import models


class BuildingOut(BaseModel):
    id: int
    address: str
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)


class ActivityOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    children: Optional[List["ActivityOut"]] = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationPhoneOut(BaseModel):
    id: int
    phone_number: str

    model_config = ConfigDict(from_attributes=True)


class OrganizationOut(BaseModel):
    id: int
    name: str
    building: BuildingOut
    phones: List[OrganizationPhoneOut]
    activities: List[ActivityOut]

    model_config = ConfigDict(from_attributes=True)
    


ActivityOut.model_rebuild()

def serialize_activity(activity: models.Activity, level: int = 1, max_level: int = 3) -> ActivityOut:
    if level > max_level:
        return None
    try:
        children = getattr(activity, "children", []) or []
    except Exception:
        children = []
    return ActivityOut(
        id=activity.id,
        name=activity.name,
        parent_id=activity.parent_id,
        children=[
            child_out
            for child in children
            if (child_out := serialize_activity(child, level + 1, max_level)) is not None
        ] if level < max_level else None
    )