import datetime
from typing import Optional

from pydantic import BaseModel

class Token(BaseModel):
    access_token: Optional[str]
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []
