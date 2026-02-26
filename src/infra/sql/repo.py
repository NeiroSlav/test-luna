from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from infra.sql.models import (
    ActivityModel,
    BuildingModel,
    OrganizationModel,
    PhoneModel,
    organization_activity,
)


class AlchemyOrganizationRepo:
    """Репозиторий для работы с организациями на SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.MAX_ACTIVITY_LEVEL = 3
        self.session = session

    # Commands

    async def add_building(
        self, address: str, latitude: float, longitude: float
    ) -> BuildingModel:
        """
        Добавить информацию о здании.
        """
        building = BuildingModel(
            address=address, latitude=latitude, longitude=longitude
        )
        self.session.add(building)
        await self.session.commit()
        await self.session.refresh(building)
        return building

    async def _calc_activity_level(self, parent_name: str) -> int:
        """
        Проверить родительский вид деятельности, рассчитать глубину вложенности.
        """
        stmt = select(ActivityModel).where(ActivityModel.name == parent_name)
        result = await self.session.execute(stmt)
        parent = result.scalar_one_or_none()
        if not parent:
            raise ValueError(f"Parent activity '{parent_name}' not found")

        if parent.level >= self.MAX_ACTIVITY_LEVEL:
            raise ValueError(
                f"Cannot add child to activity at level {parent.level}, max: {self.MAX_ACTIVITY_LEVEL}"
            )
        return parent.level + 1

    async def add_activity(
        self, name: str, parent_name: str | None = None
    ) -> ActivityModel:
        """
        Добавить вид деятельности с проверкой уровня вложенности.
        """
        parent = None
        level = 1
        if parent_name:
            level = await self._calc_activity_level(parent_name)

        activity = ActivityModel(
            name=name, parent_id=parent.id if parent else None, level=level
        )
        self.session.add(activity)
        await self.session.commit()
        await self.session.refresh(activity)
        return activity

    async def add_org(
        self,
        name: str,
        building_id: int,
        phone_numbers: list[str],
        activity_ids: list[int],
    ) -> OrganizationModel:
        """
        Добавить организацию.
        """

        building = await self.session.scalar(
            select(BuildingModel).where(BuildingModel.id == building_id)
        )
        if building is None:
            raise ValueError(f"Building {building_id} not found")

        org = OrganizationModel(name=name, building_id=building.id)
        self.session.add(org)
        await self.session.flush()

        for number in phone_numbers:
            phone = PhoneModel(organization_id=org.id, number=number)
            self.session.add(phone)

        activities = await self.session.scalars(
            select(ActivityModel).where(ActivityModel.id.in_(activity_ids))
        )
        founded_activities = activities.all()
        found_ids = {a.id for a in founded_activities}
        if len(found_ids) != len(activity_ids):
            missing = set(activity_ids) - found_ids
            raise ValueError(f"Activities {missing} not found")

        await self.session.refresh(org, ["activities"])
        org.activities.extend(founded_activities)

        await self.session.commit()

        result = await self.session.scalar(
            select(OrganizationModel)
            .where(OrganizationModel.id == org.id)
            .options(
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities),
                selectinload(OrganizationModel.building),
            )
        )
        return result

    # Querry

    async def get_orgs_by_address(self, address: str) -> list[OrganizationModel]:
        """
        Найти организации по адресу.
        """
        result = await self.session.scalars(
            select(OrganizationModel)
            .join(BuildingModel)
            .where(BuildingModel.address == address)
            .options(
                joinedload(OrganizationModel.building),
                selectinload(OrganizationModel.activities),
                selectinload(OrganizationModel.phones),
            )
        )
        return list(result)

    async def get_orgs_by_activity(self, activity: str) -> list[OrganizationModel]:
        """
        Найти организации по названию вида деятельности.
        """
        result = await self.session.scalars(
            select(OrganizationModel)
            .join(OrganizationModel.activities)
            .where(ActivityModel.name == activity)
            .options(
                joinedload(OrganizationModel.building),
                selectinload(OrganizationModel.activities),
                selectinload(OrganizationModel.phones),
            )
        )
        return list(result)

    async def get_orgs_in_coords(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
    ) -> list[OrganizationModel]:
        """
        Найти организации, здания которых находятся в квадрате координат.
        """
        result = await self.session.scalars(
            select(OrganizationModel)
            .join(BuildingModel)
            .where(
                BuildingModel.latitude.between(min_lat, max_lat),
                BuildingModel.longitude.between(min_lon, max_lon),
            )
            .options(
                joinedload(OrganizationModel.building),
                selectinload(OrganizationModel.activities),
                selectinload(OrganizationModel.phones),
            )
        )
        return list(result)

    async def get_orgs_by_activity_deep(self, activity: str) -> list[OrganizationModel]:
        """
        Найти организации, занимающиеся указанной деятельностью ИЛИ любой подкатегорией.
        """

        # все ID видов деятельности, начиная с заданного названия
        activity_cte = (
            select(ActivityModel.id)
            .where(ActivityModel.name == activity)
            .cte(name="activity_tree", recursive=True)
        )
        activity_cte = activity_cte.union_all(
            select(ActivityModel.id).where(ActivityModel.parent_id == activity_cte.c.id)
        )

        # ID организаций, связанных с любым из этих видов деятельности
        org_ids_subq = (
            select(organization_activity.c.organization_id)
            .where(organization_activity.c.activity_id.in_(select(activity_cte.c.id)))
            .subquery()
        )

        # Запрос самих организаций
        result = await self.session.scalars(
            select(OrganizationModel)
            .where(OrganizationModel.id.in_(select(org_ids_subq)))
            .options(
                joinedload(OrganizationModel.building),
                selectinload(OrganizationModel.activities),
                selectinload(OrganizationModel.phones),
            )
        )
        return list(result)

    async def get_org_by_name(self, name: str) -> OrganizationModel | None:
        """
        Найти организацию по названию.
        """
        return await self.session.scalar(
            select(OrganizationModel)
            .where(OrganizationModel.name == name)
            .options(
                joinedload(OrganizationModel.building),
                selectinload(OrganizationModel.activities),
                selectinload(OrganizationModel.phones),
            )
        )

    async def get_org_by_id(self, org_id: int) -> OrganizationModel | None:
        """
        Найти организацию по ID.
        """
        return await self.session.scalar(
            select(OrganizationModel)
            .where(OrganizationModel.id == org_id)
            .options(
                joinedload(OrganizationModel.building),
                selectinload(OrganizationModel.activities),
                selectinload(OrganizationModel.phones),
            )
        )
