from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

class Base(DeclarativeBase):
    pass

class User(Base, SQLAlchemyBaseUserTableUUID):
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)   #pmakes unique id for each post
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)  # Adds a foreign key to the User table
    caption = Column(Text)
    url = Column(String, nullable=False)    #nullable = false - must be provided when creating a post
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    use = relationship("User", back_populates="posts")  # Establishes the relationship with the User table

engine = create_async_engine(DATABASE_URL)  #Creates async connection manager
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)    #Creates factory for async database sessions, expire_on_commit=False - after commit, the objects will not be expired, so they can be used without re-querying the database

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)   #Creates tables in the database based on the defined models

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:    #sreates a session that is gona be used for deatabse operations
    async with async_session_maker() as session:
        yield session   #Yields an async session for database operations

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)