from fastapi import APIRouter, Body, Depends

from api.dependencies import get_org_repo
from infra.sql import AlchemyOrganizationRepo

activity_router = APIRouter(prefix="/activities", tags=["Activities"])


@activity_router.post("/", summary="Добавление вида деятельности")
async def add_activity(
    name: str = Body(embed=True),
    parent: str | None = Body(embed=True, default=None),
    org_repo: AlchemyOrganizationRepo = Depends(get_org_repo),
) -> None:
    await org_repo.add_activity(name=name, parent_name=parent)
