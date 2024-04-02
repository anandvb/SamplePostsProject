from sqlalchemy.orm import Session

from app.models.post_model import AddPostModel
from app.repositories.post_repository import PostRepository


class PostService:
    def __init__(self, session: Session):
        self.repo = PostRepository(session)

    def get_posts(self) -> list:
        """Get list of all posts"""
        return self.repo.get_list()

    def add_new_post(self, post_model: AddPostModel, user_id: int) -> int:
        """Adds new post"""
        return self.repo.add_post(post_model, user_id)

    def remove_post(self, post_id: int) -> bool:
        """Deletes the post"""
        return self.repo.delete_post(post_id)
