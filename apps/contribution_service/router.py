from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from utils.scheme import SUser
from utils.utils import get_current_user
from core.dependencies.dependencies import (
    get_contributions_sesison,
    get_redis_cli,
    get_rmq_connection,
)
from apps.contribution_service.service import ContributionService
from apps.contribution_service.scheme import ContributionsScheme
from aio_pika import RobustConnection
from datetime import date
from redis.asyncio import StrictRedis


contributions_router = APIRouter(
    tags=["Contributions Service"], prefix="/contributions/service/api/v1"
)


@contributions_router.post("/create-contributions/{repository_id}/")
async def create_contributions(
    repository_id: int,
    session: AsyncSession = Depends(get_contributions_sesison),
    current_user: SUser = Depends(get_current_user),
):
    service = ContributionService(session=session, current_user=current_user)
    return await service._create_contributions(repository_id=repository_id)


@contributions_router.get(
    "/get-contributions/{date}/{user_id}/", response_model=list[ContributionsScheme]
)
async def get_contributions(
    date: int, user_id: int, session: AsyncSession = Depends(get_contributions_sesison)
):
    service = ContributionService(session=session)
    return await service._get_contributions(date=date, user_id=user_id)


@contributions_router.get("/get-contribution/{date}/")
async def get_contribution(
    date: date,
    session: AsyncSession = Depends(get_contributions_sesison),
    rmq_cli: RobustConnection = Depends(get_rmq_connection),
    current_user: SUser = Depends(get_current_user),
    redis_cli: StrictRedis = Depends(get_redis_cli)
):
    service = ContributionService(
        session=session, current_user=current_user, rmq_cli=rmq_cli, redis_cli=redis_cli
    )
    return await service._get_contribute(date=date)



