from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from core.config.config import database_config


DATABASE_URL = f"postgresql+asyncpg://{database_config.username}:{database_config.password.get_secret_value()}@{database_config.host}:{database_config.port}/ContributionsDB"

contributions_engine = create_async_engine(DATABASE_URL)

async_session = sessionmaker(bind=contributions_engine, class_=AsyncSession)


class ContributionsBASE(DeclarativeBase):
    __abstract__ = True
    pass
