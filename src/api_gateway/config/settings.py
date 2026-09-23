from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    alembic_database_url: str
    sonar_token: str

    class Config:
        env_file = ".env"


settings = Settings()