from typing import Annotated

from fastapi import Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.models.generic_response import GenericResponseModel
from app.models.user_model import UserModel
from app.services.user_service import UserService
from app.utils.dependencies import get_db, get_oauth_scheme
from app.utils.helper import build_response_model

from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

user_router = InferringRouter()
oauth_scheme = get_oauth_scheme()


@cbv(user_router)
class UserController:

    def __init__(self, session: Session = Depends(get_db)):
        self.user_svc = UserService(session)

    @user_router.post('/register', summary="User registration", status_code=status.HTTP_201_CREATED,
                      response_model=GenericResponseModel)
    async def register(self, user: Annotated[UserModel, Depends()]):
        registered = self.user_svc.register(user)

        if registered:
            response_model = GenericResponseModel(status_code=status.HTTP_201_CREATED,
                                                  message="Registered successfully")
            return build_response_model(response_model)

        response_model = GenericResponseModel(status_code=status.HTTP_400_BAD_REQUEST, message="Error occurred")
        return response_model

    @user_router.post('/token', summary="Oauth token login", status_code=status.HTTP_200_OK,
                      response_model=GenericResponseModel)
    async def login(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        token = self.user_svc.get_access_token(form_data)
        if token.access_token is None:
            status_code = status.HTTP_401_UNAUTHORIZED
            response_model = GenericResponseModel(status_code=status_code, message="Token could not be generated")
            return build_response_model(response_model)

        response_model = GenericResponseModel(status_code=status.HTTP_200_OK, message="Token found", data=token)
        return build_response_model(response_model)

    @user_router.get('/logout', summary="Logout from all sessions", status_code=status.HTTP_200_OK,
                     response_model=GenericResponseModel)
    async def logout(self, request: Request):
        user = request.state.__getattr__('user')
        success = self.user_svc.logout(user.token)
        if success:
            response_model = GenericResponseModel(status_code=status.HTTP_200_OK, message="Logout successful")
            return build_response_model(response_model)

        response_model = GenericResponseModel(status_code=status.HTTP_400_BAD_REQUEST, message="Could not logout")
        return build_response_model(response_model)
