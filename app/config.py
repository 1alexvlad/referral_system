from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, model_validator


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST"] = "DEV" 

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DATABASE_URL: Optional[str] = None

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str
    TEST_DATABASE_URL: Optional[str] = None

    @model_validator(mode="after")
    def get_database_url(self):
        self.DATABASE_URL = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return self
    
    @model_validator(mode="after")
    def get_test_database_url(self):
        self.TEST_DATABASE_URL = f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
        return self
    
    model_config = ConfigDict(env_file=".env")


    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    redis_host: str
    redis_port: int
    redis_db: int


settings = Settings()