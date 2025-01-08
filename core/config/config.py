from pydantic import BaseModel, SecretStr
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()


class DatabaseConfigScheme(BaseModel):
    username: str
    password: SecretStr
    host: str
    port: int


class RedisConfigScheme(BaseModel):
    host: str
    port: int


class RmqConfigScheme(BaseModel):
    username: str
    password: SecretStr
    host: str
    port: int


class AuthSettings(BaseModel):
    secret_key: SecretStr


database_config = DatabaseConfigScheme(
    username=os.getenv("PG_USERNAME"),
    password=os.getenv("PG_PASSWORD"),
    port=os.getenv("PG_PORT"),
    host=os.getenv("PG_HOST"),
)

redis_config = RedisConfigScheme(
    host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT")
)

rmq_config = RmqConfigScheme(
    username=os.getenv("RMQ_USERNAME"),
    password=os.getenv("RMQ_PASSWORD"),
    port=os.getenv("RMQ_PORT"),
    host=os.getenv("RMQ_HOST"),
)

auth_settings = AuthSettings(secret_key=os.getenv("SECRET_KEY"))
