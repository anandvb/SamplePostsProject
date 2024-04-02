from sqlalchemy import Column, INTEGER, String, DATETIME

from app.utils.dependencies import DbBase


class UserTokenTable(DbBase):
    __tablename__ = "user_tokens"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    user_id = Column(INTEGER, nullable=False)
    username = Column(String, nullable=False)
    token = Column(String, nullable=False)
    expiry_time = Column(DATETIME, nullable=True)
