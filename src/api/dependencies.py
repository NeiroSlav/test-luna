from fastapi import Depends

from infra.sql import AlchemyOrganizationRepo, AsyncSession, get_async_session


async def get_org_repo(
    session: AsyncSession = Depends(get_async_session),
) -> AlchemyOrganizationRepo:
    return AlchemyOrganizationRepo(session)
