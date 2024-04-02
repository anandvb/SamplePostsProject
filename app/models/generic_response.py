from typing import Optional, Any

from pydantic import BaseModel


class GenericResponseModel(BaseModel):
    """Generic base model"""

    error: Optional[str] = None
    message: Optional[str] = None
    data: Any
    status_code: Optional[int] = None
