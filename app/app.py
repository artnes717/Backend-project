from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from app.db import Post, create_db_and_tables, get_async_session, User, Likes
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select, func, delete
from app.images import imagekit
# from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
# from imagekitio.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile
from app.users import auth_backend, current_active_user, fastapi_users

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        options_dict = {
            "use_unique_file_name": True,
            "tags": ["backend-upload"]
        }

        with open(temp_file_path, "rb") as f:
            file_data = f.read()

        upload_result = imagekit.files.upload(
            file=file_data,
            file_name=file.filename,
            # options=options_dict
        )

        # if upload_result.response_metadata.http_status_code == 200:
        post = Post(
            user_id = str(user.id),
            caption=caption,
            url=upload_result.url,
            file_type="video" if file.content_type.startswith("video/") else "image",
            file_name=upload_result.name,
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()



@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    posts_data = []
    for post in posts:

        likes_result = await session.execute(select(func.count()).select_from(Likes).where(Likes.post_id == post.id))
        likes_count = likes_result.scalar()
        is_liked_result = await session.execute(select(Likes).where(Likes.user_id == str(user.id), Likes.post_id == post.id))
        is_liked_result = is_liked_result.scalars().first()

        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == str(user.id),
                "like_amount": likes_count,
                "is_liked": is_liked_result is not None
            }
        )
    
    return {"posts": posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session), 
    user: User = Depends(current_active_user) ):
    try:
        # post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_id))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != str(user.id):
            raise HTTPException(status_code=403, detail="You don't have permission to delete this post")

        await session.execute(delete(Likes).where(Likes.post_id == post_id))

        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "Post deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/posts/{post_id}/like")
async def like_post(post_id: str,
                    user: User = Depends(current_active_user),
                    session: AsyncSession = Depends(get_async_session)):
    isliked = await session.execute(select(Likes).where(Likes.user_id == str(user.id), Likes.post_id == post_id))
    like = isliked.scalars().first()

    if like:
        raise HTTPException(status_code=403, detail="Post already liked")
    
    new_like = Likes(user_id=str(user.id), post_id=post_id)
    session.add(new_like)
    await session.commit()
    await session.refresh(new_like)
    
    return {"success": True, "message": "Post liked successfully"}


@app.delete("/posts/{post_id}/like")
async def delete_like(post_id: str,
                        user: User = Depends(current_active_user),
                        session: AsyncSession = Depends(get_async_session)):
    try:
        # post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Likes).where(Likes.post_id == post_id, Likes.user_id == str(user.id)))
        like = result.scalars().first()

        if not like:
            raise HTTPException(status_code=404, detail="Like not found")

        await session.delete(like)
        await session.commit()

        return {"success": True, "message": "Post unliked successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))