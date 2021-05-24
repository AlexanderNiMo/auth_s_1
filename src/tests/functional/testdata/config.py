from dataclasses import dataclass
import os


@dataclass
class Config:
    auth_host: str
    auth_port: int
    redis_host: str
    redis_port: int
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str


def get_config() -> Config:
    return Config(**{
        'auth_host': os.getenv('AUTH_HOST', 'localhost'),
        'auth_port': os.getenv('AUTH_PORT', 5000),
        'redis_host': os.getenv('REDIS_HOST', 'localhost'),
        'redis_port': os.getenv('REDIS_PORT', 6379),
        'postgres_host': os.getenv('POSTGRES_HOST', 'localhost'),
        'postgres_port': os.getenv('POSTGRES_PORT', 5432),
        'postgres_user': os.getenv('POSTGRES_USER', 'postgres'),
        'postgres_password': os.getenv('POSTGRES_PASSWORD', 'qwerty'),
    })
