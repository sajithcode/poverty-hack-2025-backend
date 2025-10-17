from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Hope4Ever API"
    env: str = "dev"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    jwt_secret: str = "replace_me"
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def sqlalchemy_async_url(self) -> str:
        # using aiomysql (pure Python)
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()
