from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreatePost(BaseModel):
    title: Annotated[str, Field(max_length=30)]
    content: str


class ReadPost(CreatePost):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    views: Annotated[int, Field(ge=0)]
    created_at: datetime
    updated_at: datetime
