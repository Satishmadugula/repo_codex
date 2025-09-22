from motor.motor_asyncio import AsyncIOMotorClient
from .config import get_settings


class Database:
    """Wrapper around MongoDB client for dependency injection."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncIOMotorClient(settings.mongodb_uri)
        self._db = self._client[settings.database_name]

    @property
    def client(self) -> AsyncIOMotorClient:
        return self._client

    @property
    def db(self):
        return self._db


db_instance: Database | None = None


def get_database() -> Database:
    global db_instance
    if db_instance is None:
        db_instance = Database()
    return db_instance
