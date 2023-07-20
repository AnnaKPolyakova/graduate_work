import os
from logging import config as logging_config
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

from tests.functional.logger import LOGGING

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env_test"), override=True)


class TestSettings(BaseSettings):
    postgres_host: str = 'localhost'
    postgres_port: int = Field(env="POSTGRES_PORT", default=5432)
    postgres_db: str = Field(env="POSTGRES_DB", default='booking')
    postgres_db_test: str = Field(
        env="POSTGRES_DB_TEST", default='booking_test'
    )
    postgres_user: str = Field(env="POSTGRES_USER", default='app')
    postgres_password: str = Field(env="POSTGRES_PASSWORD", default='123qwe')
    redis_host: str = Field(env="REDIS_HOST", default='localhost')
    redis_port: int = Field(env="REDIS_PORT", default=6379)
    redis_protocol: str = Field(env="REDIS_PROTOCOL", default='redis')
    jwt_secret_key: str = Field(
        env="JWT_SECRET_KEY",
        default='Y0QMIGwksa5OhtOBF9BczuAJ0hYMUv7esEBgMMdAuJ4V7stwxT9e'
    )
    default_limits: int = Field(env="DEFAULT_LIMITS", default=100)
    auth_host: str = Field(
        env="AUTH_HOST",
        default='AUTH_HOST=http://84.201.152.3:8001/api/v1/users/auth_check/'
    )
    page_size: int = Field(env="PAGE_SIZE", default=5)
    get_user_host: str = Field(
        env="GET_USER_HOST",
        default='http://84.201.152.3:8001/api/v1/users/{id}/'
    )
    get_film_host: str = Field(
        env="GET_FILM_HOST",
        default='http://51.250.104.105:7000/api/v1/films/{id}/'
    )
    timezone: str = Field(env="TIMEZONE", default='Europe/Moscow')
    data_format: str = Field(env="DATA_FORMAT", default="%Y-%m-%d %H:%M")
    test: bool = True
    debug: bool = False

    class Config:
        env_file = os.path.join(BASE_DIR, ".env", ".env_test")
        env_file_encoding = "utf-8"


logging_config.dictConfig(LOGGING)

test_settings = TestSettings()
