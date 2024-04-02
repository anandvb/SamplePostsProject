import os
import uuid

from dotenv import load_dotenv
from app.utils.logger import logger

logger.info("SERVER_START: setting env file")
load_dotenv(verbose=True)


def get_value(key: str, default):
    return str(os.environ.get(key, default))


class DbSettings:
    """Database related settings"""
    host = get_value("DB_HOST", "localhost")
    port = get_value("DB_PORT", 3306)
    dbname = get_value("DB_NAME", "postsdb")
    user = get_value("DB_USER", "root")
    passwd = get_value("DB_PASS", "Password@123")


class ConfigSettings:
    """Config setting for security"""
    secret = get_value("SECRET_KEY", default=str(uuid.uuid4()))
    algorithm = get_value("ALGO", "HS256")
