from redis.asyncio import StrictRedis
from core.config.config import redis_config, rmq_config
from sqlalchemy.ext.asyncio import AsyncSession
from database.contributions_db import async_session
import aio_pika


async def get_rmq_connection():
    connection = await aio_pika.connect_robust(
        f"amqp://{rmq_config.username}:{rmq_config.password.get_secret_value()}@{rmq_config.host}:{rmq_config.port}/"
    )
    try:
        yield connection
    finally:
        await connection.close()


async def get_redis_cli():
    return await StrictRedis(host=redis_config.host, port=redis_config.port)


async def get_contributions_sesison() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
