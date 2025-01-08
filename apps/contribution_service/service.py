from fastapi import HTTPException
from apps.contribution_service.models import ContributionsModel
from apps.contribution_service.scheme import ContributionsScheme, RepositoryScheme
from utils.utils import get_logger, consume_data
from utils.scheme import SUser
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Type
from aio_pika import RobustConnection
from fastapi.encoders import jsonable_encoder
from redis import StrictRedis
from sqlalchemy import select
from datetime import date
import asyncio
import httpx
import json


log = get_logger()

T = TypeVar("T")


class ContributionService:

    def __init__(
        self,
        session: AsyncSession,
        redis_cli: StrictRedis = None,
        rmq_cli: RobustConnection = None,
        current_user: SUser = None,
    ):
        self.session = session
        self.redis_cli = redis_cli
        self.rmq_cli = rmq_cli
        self.current_user = current_user

    async def _create_contributions(self, repository_id: int):
        today_contributions = (
            (
                await self.session.execute(
                    select(ContributionsModel).filter_by(
                        user_id=self.current_user.id,
                        date=date.today(),
                        repository_id=repository_id,
                    )
                )
            )
            .scalars()
            .first()
        )

        if not today_contributions:
            contributions = ContributionsModel(
                repository_id=repository_id,
                user_id=self.current_user.id,
                commit_count=1,
            )

            log.info("Createing new contributions %s", repository_id)
            self.session.add(contributions)
            await self.session.commit()
            return {"detail": "Contributions Created Succsesfully"}

        log.info("Adding contributions count or repository %s", repository_id)
        today_contributions.commit_count += 1
        await self.session.commit()
        return {"detail": "Commit count added"}

    async def _get_contributions(self, date: int, user_id: int):
        contributions = (
            (
                await self.session.execute(
                    select(ContributionsModel).filter_by(year=date, user_id=user_id)
                )
            )
            .scalars()
            .all()
        )

        if not contributions:
            log.info("Contributions not found for this year! %s", date)
            raise HTTPException(
                detail=f"Contributions not found for this year {date}", status_code=404
            )

        return [
            ContributionsScheme(**contributes.__dict__) for contributes in contributions
        ]

    async def _get_contribute(self, date: date):
        cached_data = await self._get_data_from_cahce(f"get-contributions-{date}")
        if cached_data:
            log.info("returing data from cache ")
            return [
                ContributionsScheme(**data if isinstance(data, dict) else json.loads(data))
                for data in cached_data
            ]

        contributions = (await self.session.execute(
            select(ContributionsModel)
            .filter_by(date=date)
        )).scalars().all()


        if not contributions:
            log.info("Contributions not found for this data")
            raise HTTPException(detail="Contributions not found", status_code=404)

        await asyncio.gather(
            *[
                self._request_to_url(
                    f"http://localhost:8082/repository/service/api/v1/get-repository/{contributes.repository_id}/"
                )
                for contributes in contributions
            ]
        )


        repository_data = await asyncio.gather(
            *[
                consume_data(
                    f"get-repository-{contributes.repository_id}",
                    connection=self.rmq_cli,
                )
                for contributes in contributions
            ]
        )


        repository = [
            RepositoryScheme(**(data) if isinstance(data, dict) else json.loads(data)) for data in repository_data
        ]


        response = [
            ContributionsScheme(**contributions.__dict__, repository=repository)
            for contributions, repository in zip(contributions, repository)
        ]

        serialized_data = jsonable_encoder(response)


        await self.redis_cli.setex(f"get-contributions-{date}", 300, json.dumps(serialized_data))

        return response
    


    async def _request_to_url(self, url):
        headers = {}
        if self.current_user and self.current_user.token:
            headers["Authorization"] = f"Bearer {self.current_user.token}"

        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            response = await client.get(url, headers=headers)
            return response


        
    async def _get_data_from_cahce(self, key):
        cached_data = await self.redis_cli.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None
    

    