from db import async_session
from models import Post


async def update_view(post_id):
    async with async_session() as session:
        post = await session.get(Post, post_id)
        if not post:
            return
        post.views += 1
        await session.commit()
