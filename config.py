import os

from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    POSTGRES_DB: str = os.getenv("SANIC_POSTGRES_DB", "payments")
    POSTGRES_USER: str = os.getenv("SANIC_POSTGRES_USER", "admin")
    POSTGRES_PASSWORD: str = os.getenv("SANIC_POSTGRES_PASSWORD", "2204156")
    POSTGRES_HOST: str = os.getenv("SANIC_POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("SANIC_POSTGRES_PORT", "5432")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )


class SecurityConfig(BaseSettings):
    SECRET_KEY: str = os.getenv("SANIC_SECRET_KEY", "gfdmhghif38yrf9ew0jkf32")
    JWT_EXPIRATION: int = int(os.getenv("SANIC_JWT_EXPIRATION", 3600))
    ALGORITHM: str = os.getenv("SANIC_ALGORITHM", "HS256")


class AppConfig(BaseSettings):
    DEBUG: bool = bool(os.getenv("SANIC_DEBUG", True))
    HOST: str = os.getenv("SANIC_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("SANIC_PORT", 8080))
    WORKERS: int = int(os.getenv("SANIC_WORKERS", 1))
    ACCESS_LOG: bool = bool(os.getenv("SANIC_ACCESS_LOG", True))
    DEV: bool = bool(os.getenv("SANIC_DEV", True))
    AUTO_RELOAD: bool = bool(os.getenv("SANIC_AUTO_RELOAD", True))


class TestUsersConfig(BaseSettings):
    TEST_ADMIN_EMAIL: str = os.getenv("SANIC_WORKERSTEST_ADMIN_EMAIL", "admin@test.com")
    TEST_ADMIN_PASSWORD: str = os.getenv("SANIC_WORKERSTEST_ADMIN_PASSWORD", "admin123")
    TEST_USER_EMAIL: str = os.getenv("SANIC_WORKERSTEST_USER_EMAIL", "user@test.com")
    TEST_USER_PASSWORD: str = os.getenv("SANIC_WORKERSTEST_USER_PASSWORD", "user123")


class Config:
    def __init__(self) -> None:
        self.database = DatabaseConfig()
        self.security = SecurityConfig()
        self.app = AppConfig()
        self.test_users = TestUsersConfig()

    @property
    def DATABASE_URL(self) -> str:
        return self.database.database_url

    @property
    def SECRET_KEY(self) -> str:
        return self.security.SECRET_KEY

    @property
    def JWT_EXPIRATION(self) -> int:
        return self.security.JWT_EXPIRATION

    @property
    def ALGORITHM(self) -> str:
        return self.security.ALGORITHM

    @property
    def DEBUG(self) -> bool:
        return self.app.DEBUG

    @property
    def DEV(self) -> bool:
        return self.app.DEV

    @property
    def HOST(self) -> str:
        return self.app.HOST

    @property
    def PORT(self) -> int:
        return self.app.PORT

    @property
    def WORKERS(self) -> int:
        return self.app.WORKERS

    @property
    def ACCESS_LOG(self) -> bool:
        return self.app.ACCESS_LOG

    @property
    def AUTO_RELOAD(self) -> bool:
        return self.app.AUTO_RELOAD

    @property
    def TEST_ADMIN_EMAIL(self) -> str:
        return self.test_users.TEST_ADMIN_EMAIL

    @property
    def TEST_ADMIN_PASSWORD(self) -> str:
        return self.test_users.TEST_ADMIN_PASSWORD

    @property
    def TEST_USER_EMAIL(self) -> str:
        return self.test_users.TEST_USER_EMAIL

    @property
    def TEST_USER_PASSWORD(self) -> str:
        return self.test_users.TEST_USER_PASSWORD


config = Config()
