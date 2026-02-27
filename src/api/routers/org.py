from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_org_repo
from api.dto import OrgDTO
from api.schemas import OrgSchema
from infra.sql import AlchemyOrganizationRepo

org_router = APIRouter(prefix="/organizations", tags=["Organizations"])


@org_router.post("/", summary="Добавление организации")
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


# - вывод информации об организации по её идентификатору
@org_router.get("/{org_id}", summary="Поиск организации по id")
async def get_org(
    org_id: int,
    org_repo: AlchemyOrganizationRepo = Depends(get_org_repo),
) -> OrgDTO | None:
    org = await org_repo.get_org_by_id(org_id)
    if not org:
        raise HTTPException(404, f"Organiszation id {org_id} not found")
    return OrgDTO.from_infra(org)


SEARCH_SUMMARY = "Поиск организаций по параметрам"

SEARCH_DESCRIPTION = """
Поиск организаций по различным критериям:
- адрес
- название
- вид деятельности
- расположение

### Поиск по типам деятельности
Если propagate=true - поиск производится по всем подтипам.

### Поиск по координатам
Стандартный радиус — 1 км.
"""


@org_router.get("/", description=SEARCH_DESCRIPTION, summary=SEARCH_SUMMARY)
async def get_orgs_by(
    #
    address: str = Query(default=None, description="Адрес здания организации"),
    #
    name: str = Query(default=None, description="Имя или часть имени организации"),
    #
    activity: str = Query(default=None, description="Тип деятельности организации"),
    propagate: bool = Query(default=False, description="Искать ли в дочерних типах"),
    #
    lat: float | None = Query(None, description="Широта центра поиска"),
    lon: float | None = Query(None, description="Долгота центра поиска"),
    radius: float = Query(1.0, gt=0, description="Радиус поиска (км)"),
    #
    org_repo: AlchemyOrganizationRepo = Depends(get_org_repo),
) -> list[OrgDTO]:

    org_models = await org_repo.search(
        address=address,
        name=name,
        activity=activity,
        propagate=propagate,
        lat=lat,
        lon=lon,
        radius=radius,
    )
    return [OrgDTO.from_infra(om) for om in org_models]
