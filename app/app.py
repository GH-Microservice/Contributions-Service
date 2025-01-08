from fastapi import FastAPI
from apps.contribution_service.router import contributions_router
from database.contributions_db import ContributionsBASE, contributions_engine


app = FastAPI(title="Contributions API SERVICE")


app.include_router(contributions_router)


async def create_teables():
    async with contributions_engine.begin() as conn:
        await conn.run_sync(ContributionsBASE.metadata.create_all)


@app.on_event("startup")
async def on_startup():
    return await create_teables()
