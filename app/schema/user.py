from typing import List

from sqlalchemy import Column, INTEGER, String
from sqlalchemy.orm import relationship, Mapped

#from app.schema.post import PostTable
from app.utils.dependencies import DbBase


class UserTable(DbBase):
    __tablename__ = "users"

    id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    # relationship
    posts = relationship("PostTable", back_populates="user")
