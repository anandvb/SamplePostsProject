from cachetools import cached, TTLCache
from sqlalchemy.orm import Session

from app.models.post_model import AddPostModel, ShowPostsModel
from app.repositories.base_repository import BaseRepository
from app.schema.post import PostTable
from app.utils.logger import logger


class PostRepository(BaseRepository):
    """Class to work for posts"""

    def __init__(self, session: Session):
        super().__init__(session)

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def get_list(self) -> list[ShowPostsModel]:
        """Get list of posts for all users"""
        posts = self._session.query(PostTable).all()
        model_list = []

        for post in posts:
            model_list.append(
                ShowPostsModel(
                    id=post.id,
                    title=post.title,
                    description=post.description,
                    user=post.user.email,
                )
            )

        return model_list

    def add_post(self, post_model: AddPostModel, user_id: int) -> int:
        """Adds new post"""
        post_table_model = PostTable(**post_model.dict())
        post_table_model.user_id = user_id
        try:
            post_id: int = 0
            self._session.add(post_table_model)
            self._session.flush()
            post_id = post_table_model.id

            self._session.commit()
        except Exception as ex:
            logger.error(ex)

        return post_id

    def delete_post(self, post_id: int) -> bool:
        """Deletion of existing post"""
        delete_success = False
        post = self._session.get(PostTable, post_id)
        if post is not None:
            self._session.delete(post)
            self._session.commit()
            delete_success = True

        return delete_success
