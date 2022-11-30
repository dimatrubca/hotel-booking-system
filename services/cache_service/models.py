from typing import Optional
from pydantic import BaseModel

class CacheRequest(BaseModel):
    url: str
    data: str

class CachedResponse(BaseModel):
    success: bool
    response: Optional[str]