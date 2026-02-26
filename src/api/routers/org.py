from fastapi import APIRouter, Depends, Query

from api.dependencies import get_org_repo
from api.dto import OrgDTO
from api.schemas import OrgSchema
from infra.sql import AlchemyOrganizationRepo

org_router = APIRouter(prefix="/organizations")


@org_router.get("/test")
async def test_route() -> dict[str, bool]:
    return {"ok": True}


@org_router.post("/")
async def add_org(
    schema: OrgSchema,
    org_repo: AlchemyOrganizationRepo = Depends(get_org_repo),
) -> None:
    await org_repo.add_org(
        name=schema.name,
        building_id=schema.building_id,
        phone_numbers=schema.phone_numbers,
        activity_ids=schema.activity_ids,
    )


# 3 вывод информации об организации по её идентификатору
@org_router.get("/{org_id}")
async def get_org(
    org_id: int,
    org_repo: AlchemyOrganizationRepo = Depends(get_org_repo),
) -> OrgDTO | None:
    org = await org_repo.get_org_by_id(org_id)
    if org:
        return OrgDTO.from_orm_model(org)


# искать организации по виду деятельности. Например, поиск по виду деятельности «Еда», которая находится на первом уровне дерева, и чтобы нашлись все организации, которые относятся к видам деятельности, лежащим внутри. Т.е. в результатах поиска должны отобразиться организации с видом деятельности Еда, Мясная продукция, Молочная продукция.
# ограничить уровень вложенности деятельностей 3 уровням


# 1 список всех организаций находящихся в конкретном здании
# 2 список всех организаций, которые относятся к указанному виду деятельности
# 3 список организаций, которые находятся в заданном радиусе/прямоугольной области относительно указанной точки на карте. список зданий
# 4 поиск организации по названию
@org_router.get("/")
async def get_orgs_by(
    address: str = Query(default=None),
    #
    activity: str = Query(default=None),
    #
    near: tuple[float, float] = Query(default=None),
    radius: float = Query(default=None),
    #
    name: str = Query(default=None),
    #
    org_repo: AlchemyOrganizationRepo = Depends(get_org_repo),
) -> list[OrgDTO]:

    org_models = await org_repo.get_orgs_by_address(address)
    return [OrgDTO.from_orm_model(om) for om in org_models]
