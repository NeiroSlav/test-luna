from sqlalchemy import ColumnElement, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from infra.sql.models import ActivityModel, BuildingModel, OrganizationModel, PhoneModel
from infra.sql.utils import get_bounding_box


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

    async def _assert_valid_parent(self, parent_name: str) -> ActivityModel:
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
        return parent

    async def add_activity(
        self, name: str, parent_name: str | None = None
    ) -> ActivityModel:
        """
        Добавить вид деятельности с проверкой уровня вложенности.
        """
        parent_id = None
        level = 1
        if parent_name:
            parent = await self._assert_valid_parent(parent_name)
            parent_id = parent.id
            level = parent.level + 1

        activity = ActivityModel(name=name, parent_id=parent_id, level=level)
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

    async def search(
        self,
        *,
        address: str | None = None,
        #
        name: str | None = None,
        #
        activity: str | None = None,
        propagate: bool = False,
        #
        lat: float | None = None,
        lon: float | None = None,
        radius: float | None = None,
    ) -> list[OrganizationModel]:
        """
        Найти организацию по разным параметрам.
        """

        stmt = select(OrganizationModel).distinct()

        # связанные сущности
        stmt = stmt.options(
            joinedload(OrganizationModel.building),
            selectinload(OrganizationModel.activities),
            selectinload(OrganizationModel.phones),
        )

        # building если нужен адрес или координаты
        if address or (lat is not None and lon is not None):
            stmt = stmt.join(BuildingModel)

        # activities если нужен фильтр по деятельности
        if activity:
            stmt = stmt.join(OrganizationModel.activities)

        conditions: list[ColumnElement[bool]] = []

        # Фильтр по адресу
        if address:
            conditions.append(BuildingModel.address == address)
        # Фильтр по названию
        if name:
            conditions.append(OrganizationModel.name.ilike(f"%{name}%"))
        # Фильтр по деятельности
        if activity:
            deep_activity_stmt = self._get_activity_stmt(activity, propagate)
            conditions.append(deep_activity_stmt)
        # Фильтр по координатам
        if lat is not None and lon is not None and radius is not None:
            coords_stmt = self._get_coords_stmt(lat, lon, radius)
            conditions.append(coords_stmt)

        if conditions:
            stmt = stmt.where(*conditions)

        result = await self.session.scalars(stmt)
        return list(result)

    # Utils

    def _get_activity_stmt(self, activity: str, propagate: bool) -> ColumnElement[bool]:
        """Собрать условие поиска по типу деятельности."""
        if not propagate:
            return ActivityModel.name == activity

        activity_cte = (
            select(ActivityModel.id)
            .where(ActivityModel.name == activity)
            .cte(name="activity_tree", recursive=True)
        )
        activity_cte = activity_cte.union_all(
            select(ActivityModel.id).where(ActivityModel.parent_id == activity_cte.c.id)
        )
        return ActivityModel.id.in_(select(activity_cte.c.id))

    def _get_coords_stmt(
        self, lat: float, lon: float, radius: float
    ) -> ColumnElement[bool]:
        """Собрать условие поиска по координатам."""

        min_lat, max_lat, min_lon, max_lon = get_bounding_box(lat, lon, radius)
        return and_(
            BuildingModel.latitude.between(min_lat, max_lat),
            BuildingModel.longitude.between(min_lon, max_lon),
        )
