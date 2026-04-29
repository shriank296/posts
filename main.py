from contextlib import asynccontextmanager
from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import engine, get_session
from models import Base, Post
from schemas import CreatePost, ReadPost
from utils import update_view


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
    post_in: CreatePost,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    post_obj = Post(**post_in.model_dump())
    session.add(post_obj)
    await session.commit()
    await session.refresh(post_obj)
    return post_obj


@app.get("/posts")
async def get_posts(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[ReadPost]:
    stmt = select(Post)
    all_posts = (await session.execute(stmt)).scalars().all()
    return all_posts


@app.post("/posts/{post_id}/view", response_model=ReadPost)
async def view_post(
    post_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    background_task: BackgroundTasks,
):
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    background_task.add_task(update_view, post_id)
    return post
