from pydantic_settings import BaseSettings
from pydantic import EmailStr, ConfigDict, field_validator

class Settings(BaseSettings):
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str

    SECRET_JWT: str
    ALGORITHM_JWT: str

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    DB_URL: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str | None

    model_config = ConfigDict(extra='ignore', env_file='.env', env_file_encoding='utf-8')

    @field_validator('ALGORITHM_JWT')
    def validate_algo(cls, value):
        accepted = ['HS256', 'HS512']
        if value not in accepted:
            raise ValueError(f'Accepted algorithms are: {accepted}')
        return value

config = Settings()
