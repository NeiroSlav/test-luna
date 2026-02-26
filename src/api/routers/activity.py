from fastapi import APIRouter, Body, Depends

from api.dependencies import get_org_repo
from infra.sql import AlchemyOrganizationRepo

activity_router = APIRouter(prefix="/activities")


@activity_router.post("/")
async def add_activity(
    name: str = Body(embed=True),
    parent: str | None = Body(embed=True),
    org_repo: AlchemyOrganizationRepo = Depends(get_org_repo),
) -> None:
    await org_repo.add_activity(name=name, parent_name=parent)
