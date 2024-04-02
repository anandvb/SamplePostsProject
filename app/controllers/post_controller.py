from fastapi import Depends, Request
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session
from starlette import status

from app.models.generic_response import GenericResponseModel
from app.models.post_model import AddPostModel
from app.services.post_service import PostService
from app.utils.dependencies import get_db
from app.utils.helper import build_response_model

post_router = InferringRouter()


@cbv(post_router)
class PostController:
    """Class to handle all post related operations"""

    def __init__(self, session: Session = Depends(get_db)):
        self.post_service = PostService(session)

    @post_router.get(
        "/list",
        summary="Show all posts",
        status_code=status.HTTP_200_OK,
        response_model=GenericResponseModel,
    )
    async def index(self):
        """Show all posts"""
        posts = self.post_service.get_posts()
        if len(posts) > 0:
            message = "results found"
            data = posts
        else:
            message = "No data found"
            data = []

        response_model = GenericResponseModel(
            data=data, message=message, status_code=status.HTTP_200_OK
        )
        return build_response_model(response_model)

    @post_router.post(
        "/add",
        summary="Add new post",
        status_code=status.HTTP_201_CREATED,
        response_model=GenericResponseModel,
    )
    async def add(self, request: Request, post_model: AddPostModel):
        """Add new post"""
        logged_in_user = request.state.user.user_id
        post_id = self.post_service.add_new_post(post_model, logged_in_user)

        if post_id > 0:
            status_code = status.HTTP_201_CREATED
            data = post_id
            message = "Post created successfully"
        else:
            status_code = status.HTTP_404_NOT_FOUND
            message = "Error occurred while creating new post"
            data = 0

        response_model = GenericResponseModel(
            data=data, message=message, status_code=status_code
        )
        return build_response_model(response_model)

    @post_router.get(
        "/remove/{post_id}",
        status_code=status.HTTP_202_ACCEPTED,
        response_model=GenericResponseModel,
    )
    async def remove(self, post_id):
        """Removing the seleted post"""
        removed = self.post_service.remove_post(post_id)
        if removed:
            status_code = status.HTTP_202_ACCEPTED
            message = "The post has been removed"
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            message = "Sorry, the post could not be removed"

        response_model = GenericResponseModel(message=message, status_code=status_code)
        return build_response_model(response_model)
