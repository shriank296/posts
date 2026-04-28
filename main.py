from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from db import engine, get_session
from models import Base, Post
from schemas import CreatePost, ReadPost


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def index():
    return {"hello": "world"}


@app.post("/create-post", response_model=ReadPost)
async def create_post(
    post_in: CreatePost, session: Annotated[AsyncSession, Depends(get_session)]
):
    post_obj = Post(**post_in.model_dump())
    session.add(post_obj)
    await session.commit()
    await session.refresh(post_obj)
    return post_obj
