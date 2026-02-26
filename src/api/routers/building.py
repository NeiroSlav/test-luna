from fastapi import APIRouter, Depends

from api.dependencies import get_org_repo
from api.schemas import BuildingSchema
from infra.sql import AlchemyOrganizationRepo

building_router = APIRouter(prefix="/building")


@building_router.post("/")
async def add_org(
    schema: BuildingSchema,
    org_repo: AlchemyOrganizationRepo = Depends(get_org_repo),
) -> None:
    await org_repo.add_building(
        address=schema.address,
        latitude=schema.latitude,
        longitude=schema.longtitude,
    )
