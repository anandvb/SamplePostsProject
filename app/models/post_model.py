from typing import Optional, Any

from pydantic import BaseModel, Field


class AddPostModel(BaseModel):
    title: str = Field(min_length=5, max_length=50)
    description: str = Field(default=None, max_length=150)


class ShowPostsModel(BaseModel):
    id: int
    title: Optional[str]
    description: Optional[str]
    user: Optional[Any]
