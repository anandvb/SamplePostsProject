from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.settings import ConfigSettings
from app.models.user_model import (
    UserModel,
    ActiveSessionModel,
    UserInRequestModel,
    UserGenericModel,
)
from app.repositories.base_repository import BaseRepository
from app.schema.user import UserTable
from app.schema.user_token import UserTokenTable
from app.utils.dependencies import get_pwd_context, get_connection


class UserRepository(BaseRepository):
    """Class to work with db related operations"""

    def __init__(self, session: Session):
        super().__init__(session)

    def register(self, user: UserModel) -> bool:
        """Register user if not exists"""
        db_record = (
            self._session.query(UserTable)
            .where(UserTable.email == user.username)
            .first()
        )
        if db_record is None:
            user_rec = UserTable()
            user_rec.email = user.username
            user_rec.password = bcrypt.hash(user.password)

            self._session.add(user_rec)
            self._session.commit()

            return True
        else:
            return False

    def generate_token(self, data: dict, expiry_delta):
        """Generate new access token"""
        to_encode = data.copy()
        expiry = expiry_delta
        to_encode.update({"exp": expiry})
        encoded_jwt = jwt.encode(
            to_encode, ConfigSettings.secret, algorithm=ConfigSettings.algorithm
        )
        return encoded_jwt

    def get_user(self, username: str) -> Optional[UserGenericModel]:
        """Get user for the requested email"""
        db_user = (
            self._session.query(UserTable).where(UserTable.email == username).first()
        )
        if db_user is not None:
            user = UserGenericModel()
            user.username = db_user.email
            user.password = db_user.password

            return user

        return None

    def is_password_correct(self, form_date: OAuth2PasswordRequestForm = Depends()):
        """Check if user exists for the given password"""
        user = self.get_user(form_date.username)
        pwd_context = get_pwd_context()

        if user is None or not pwd_context.verify(form_date.password, user.password):
            return False
        return True

    def get_access_token(self, form_data: OAuth2PasswordRequestForm = Depends()):
        """Get access token for the requested user"""
        access_token_expires = datetime.utcnow() + timedelta(minutes=30)
        access_token = self.generate_token(
            data={"sub": form_data.username}, expiry_delta=access_token_expires
        )
        return access_token

    def authenticate(self, token: str) -> UserInRequestModel:
        """Authenticate user based on token
        :param token access token
        :returns user UserInRequestModel
        :exception HTTPException exception
        """
        try:
            payload = jwt.decode(
                token, ConfigSettings.secret, algorithms=[ConfigSettings.algorithm]
            )
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            # check if pwd is expired
            expiry_time = payload.get("exp")

            if expiry_time is None or expiry_time < datetime.utcnow().timestamp():
                # delete from active sessions
                self.logout(token)
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail="Login failed or expired",
                )

            # Check feasibility of using session
            if not isinstance(self._session, Session):
                conn = get_connection()
                with conn.begin() as connection:
                    active_session = connection.execute(
                        select(UserTokenTable).where(
                            UserTokenTable.username == username
                        )
                    ).first()
            else:
                active_session = (
                    self._session.query(UserTokenTable)
                    .where(UserTokenTable.username == username)
                    .first()
                )

            if active_session is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User session not found or expired",
                )

            current_user = UserInRequestModel(
                user_id=active_session.user_id,
                username=active_session.username,
                token=token,
            )

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, try again",
            )

        return current_user

    def register_token_in_session(self, token: str):
        """Registers token in session"""
        try:
            payload = jwt.decode(
                token, ConfigSettings.secret, algorithms=[ConfigSettings.algorithm]
            )
            user, expiry = payload.get("sub"), payload.get("exp")
            exp_time = datetime.utcfromtimestamp(expiry)
            user_id = 0

            db_user = (
                self._session.query(UserTable).where(UserTable.email == user).first()
            )
            if db_user is not None:
                user_id = db_user.id

            active_session = ActiveSessionModel(
                user_id=user_id, username=user, access_token=token, expiry_time=exp_time
            )

            user_token = UserTokenTable(
                user_id=user_id, username=user, token=token, expiry_time=exp_time
            )

            self._session.add(user_token)
            self._session.commit()

            # if result is not None:
            return active_session

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Unknown error occurred"
            )

    def is_active_session(self, user_name: str) -> bool:
        """Is there any session active
        @:param user_name name of user
        @:returns boolean
        """
        db_user = (
            self._session.query(UserTokenTable)
            .where(UserTokenTable.username == user_name)
            .first()
        )
        if db_user is None:
            return False

        token = db_user.token
        try:
            payload = jwt.decode(
                token, ConfigSettings.secret, algorithms=[ConfigSettings.algorithm]
            )
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            # check if pwd is expired
            expiry_time = payload.get("exp")
            if expiry_time is None or expiry_time < datetime.utcnow().timestamp():
                return False

        except JWTError:
            # delete the token from db
            # user_token = UserTokenTable(token=token)
            self._session.delete(db_user)
            self._session.commit()

            return False
        return True

    def get_active_access_token(self, user_name: str):
        """Get active access token"""
        db_user = (
            self._session.query(UserTokenTable)
            .where(UserTokenTable.username == user_name)
            .first()
        )
        if db_user is None:
            return None
        return db_user.token

    def logout(self, token: str) -> bool:
        """Deletes token from repo"""
        db_user = (
            self._session.query(UserTokenTable)
            .where(UserTokenTable.token == token)
            .first()
        )
        if db_user is not None:
            self._session.delete(db_user)
            self._session.commit()

        return True
