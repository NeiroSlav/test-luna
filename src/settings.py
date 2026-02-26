from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):

    POSTGRES_HOST: str = "postgres-db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @property
    def database_url(self) -> str:
        _url = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
        return _url.format(
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            db=self.POSTGRES_DB,
        )


def get_settings() -> Settings:
    return Settings()  # type: ignore
