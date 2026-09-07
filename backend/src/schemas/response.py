from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ErrorDetailSchema(BaseModel):
    """
    Sub-payload structure detailing parameter errors or validation failures.
    """
    field: str
    issue: str

class APIErrorSchema(BaseModel):
    """
    Error payload schema mapping details to client interfaces.
    """
    code: str
    message: str
    details: Optional[Any] = None

class APIResponse(BaseModel, Generic[T]):
    """
    Standard successful envelope structure for all API outputs.
    """
    success: bool = True
    data: Optional[T] = None

class APIErrorResponse(BaseModel):
    """
    Standard error envelope structure for all system exceptions.
    """
    success: bool = False
    error: APIErrorSchema
