from fastapi import APIRouter

org_router = APIRouter()


@org_router.get("/test")
async def test_route() -> dict[str, bool]:
    return {"ok": True}
