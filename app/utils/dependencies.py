from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from app.config.settings import DbSettings
from app.utils.logger import logger

DbBase = declarative_base()


def get_connection() -> Engine:
    """Gets connection from db"""
    uri = URL.create(
        "mysql+pymysql",
        username=DbSettings.user,
        password=DbSettings.passwd,  # plain (unescaped) text
        host=DbSettings.host,
        database=DbSettings.dbname,
        port=DbSettings.port
    )

    db_engine = create_engine(uri)
    return db_engine


def get_db() -> Session:
    """Gets db object for the new connection"""
    try:
        engine = get_connection()
        session_maker = sessionmaker(
            autoflush=False, bind=engine, expire_on_commit=True
        )
        session_local: Session = session_maker()
        yield session_local

    except Exception as e:
        logger.error(e)
        logger.error("Error occurred while establishing connection")

    finally:
        # close connection
        if session_local:
            session_local.close()


def get_pwd_context() -> CryptContext:
    """Get password context for bcrypt"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context


def get_oauth_scheme() -> OAuth2PasswordBearer:
    """OAuth 2.0 scheme"""
    return OAuth2PasswordBearer(
        tokenUrl="token",
        scopes={"me": "Read information about the current user.", "items": "Read items."},
    )
