from pydantic import BaseModel
from datetime import datetime
from typing import List, Annotated, Optional

class NoteCreate(BaseModel):
    content: str
    tags: list[str]

class NoteResponse(BaseModel):
    id: int
    content: str
    tags: List[str]
    createdAt: datetime
    lastupdated: datetime


class NoteUpdateRequest(BaseModel):
    content: Optional[str] = None
    tags: Optional[List[str]] = None


