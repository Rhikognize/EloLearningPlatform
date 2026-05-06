from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Baza de date
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_URL: str

    # Securitate / JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # Setări rețea
    CORS_ORIGIN: str

    model_config = SettingsConfigDict(
        env_file="../.env", env_file_encoding='utf-8')


settings = Settings()
