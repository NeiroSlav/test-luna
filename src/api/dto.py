from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from infra.sql import OrganizationModel


class BaseDTO(BaseModel):
    """
    Базовая модель DTO с автоматическим переводом полей в camelCase.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class OrgDTO(BaseDTO):
    """
    Публичный DTO организации.
    """

    id: int
    name: str
    address: str
    phone_numbers: list[str]
    activities: list[str]

    @classmethod
    def from_orm_model(cls, orm_model: OrganizationModel) -> "OrgDTO":
        """Фабричный метод создания из ORM-модели."""
        return cls(
            id=orm_model.id,
            name=orm_model.name,
            address=orm_model.building.address,
            phone_numbers=[n.number for n in orm_model.phones],
            activities=[a.name for a in orm_model.activities],
        )
