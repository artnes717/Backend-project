from collections.abc import AsyncGenerator 
import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID # ? 
from sqlalchemy import Column, String, Text, DateTime
import uuid as uuid_pkg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends

DATABESE_URL = "sqlite+aiosqlite:///./test.db"

class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    posts = relationship("Post", back_populates="user")
    # likes = relationship("Likes", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(String, primary_key=True, default=lambda: str(uuid_pkg.uuid4()))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="posts")

class Likes(Base):
    __tablename__ = "likes"

    id = Column(String, primary_key=True, default=lambda: str(uuid_pkg.uuid4()))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False)


engine = create_async_engine(DATABESE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)