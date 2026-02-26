from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    """Базовая схемма с поддержкой camelCase полей."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class BuildingSchema(BaseSchema):
    """Схемма добавления здания."""

    address: str
    longtitude: float
    latitude: float


class OrgSchema(BaseSchema):
    """Схемма добавления организации."""

    name: str
    building_id: int
    phone_numbers: list[str]
    activity_ids: list[int]
