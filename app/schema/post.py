from sqlalchemy import Column, INTEGER, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.post_model import ShowPostsModel
from app.utils.dependencies import DbBase
from app.utils.logger import logger


class PostTable(DbBase):
    __tablename__ = "posts"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    description = Column(String(150), nullable=False)
    user_id = Column(INTEGER, ForeignKey("users.id"))

    # relations
    user = relationship("UserTable", back_populates="posts")

    # ORM to model conversion
    def to_model(self) -> ShowPostsModel:
        """ORM to pydantic model"""
        post_model = None
        try:
            post_model = ShowPostsModel.validate(self.__dict__)
        except Exception as e:
            print(e)
            logger.error("Error occurred during transformation")

        return post_model
