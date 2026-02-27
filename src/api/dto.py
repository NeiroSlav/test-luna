from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from infra.sql import BuildingModel, OrganizationModel


class BaseDTO(BaseModel):
    """
    Базовая модель DTO с автоматическим переводом полей в camelCase.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class BuildingDTO(BaseDTO):
    """Публичный DTO здания."""

    id: int
    coords: tuple[float, float]
    address: str

    @classmethod
    def from_infra(cls, orm_model: BuildingModel) -> "BuildingDTO":
        """Фабричный метод создания из ORM-модели."""
        return cls(
            id=orm_model.id,
            coords=(orm_model.latitude, orm_model.longitude),
            address=orm_model.address,
        )


class OrgDTO(BaseDTO):
    """
    Публичный DTO организации.
    """

    id: int
    name: str
    building: BuildingDTO
    phone_numbers: list[str]
    activities: list[str]

    @classmethod
    def from_infra(cls, orm_model: OrganizationModel) -> "OrgDTO":
        """Фабричный метод создания из ORM-модели."""
        return cls(
            id=orm_model.id,
            name=orm_model.name,
            building=BuildingDTO.from_infra(orm_model.building),
            phone_numbers=[n.number for n in orm_model.phones],
            activities=[a.name for a in orm_model.activities],
        )
