from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models.token_model import Token
from app.models.user_model import UserModel
from app.repositories.user_repository import UserRepository


class UserService:
    """Business logic related to user mgmt"""

    def __init__(self, session: Session):
        self.user_repo = UserRepository(session)

    def register(self, user: UserModel):
        """Registers user"""
        return self.user_repo.register(user)

    def get_access_token(self, form_data: OAuth2PasswordRequestForm = Depends()):
        """Get access token"""
        if not self.user_repo.is_password_correct(form_data):
            return Token(access_token=None, token_type="bearer")
        if not self.user_repo.is_active_session(form_data.username):
            access_token = self.user_repo.get_access_token(form_data)
            if access_token is not None:
                self.user_repo.register_token_in_session(access_token)
                return Token(access_token=access_token, token_type="bearer")

        access_token = self.user_repo.get_active_access_token(form_data.username)
        return Token(access_token=access_token, token_type="bearer")

    def authenticate(self, token: str):
        """Authenticate token"""
        return self.user_repo.authenticate(token)

    def register_token_in_session(self, token: str):
        """Active session registration"""
        return self.user_repo.register_token_in_session(token)

    def logout(self, token: str):
        """Logout"""
        return self.user_repo.logout(token)

    def is_session_active(self, user_name: str):
        """Active?"""
        return self.user_repo.is_active_session(user_name)
