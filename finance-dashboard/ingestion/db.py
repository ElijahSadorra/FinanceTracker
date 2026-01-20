import os
from dataclasses import dataclass
from typing import Optional

import psycopg2
from psycopg2.extensions import connection


@dataclass
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str


def load_db_config() -> DatabaseConfig:
    return DatabaseConfig(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        name=os.getenv("POSTGRES_DB", "finance"),
        user=os.getenv("POSTGRES_USER", "finance_app"),
        password=os.getenv("POSTGRES_PASSWORD", "change_me"),
    )


def get_connection(db_url: Optional[str] = None) -> connection:
    if db_url:
        return psycopg2.connect(db_url)

    config = load_db_config()
    return psycopg2.connect(
        host=config.host,
        port=config.port,
        dbname=config.name,
        user=config.user,
        password=config.password,
    )
