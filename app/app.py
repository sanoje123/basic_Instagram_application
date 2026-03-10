from fastapi import FastAPI, HTTPException, Form, Depends, File, UploadFile
from .schema import PostCreate, PostResponse
from app.db import create_db_and_tables, get_async_session, Post
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select

@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan= lifespan)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),    #caption comes from a form field, not JSON
    session: AsyncSession = Depends(get_async_session)  #Before running this function, give me a database session.
):
    post = Post(
        caption=caption,
        url="dummy url",
        file_type="photo",
        file_name="name"
    )
    
    session.add(post)   #This tells SQLAlchemy:"Add this object to the transaction." - It does NOT write to database yet.
    await session.commit()  #Now SQLAlchemy sends the query to the database. Equivalent SQL: INSERT INTO post (...) VALUES (...)
    await session.refresh(post) #After commit, the post object is updated with any new data from the database, such as the generated id. This is important for getting the id of the newly created post.
    return post

@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
    ):
    result  = await session.execute(select(Post).order_by(Post.date.desc()))    #This is how you execute a query with SQLAlchemy. select(Post) creates a SELECT statement for the Post model, ordered_by(Post.created_at.desc()) sorts the results by creation date in descending order. The result variable will contain the query results, which can be accessed using result.scalars().all() to get a list of Post objects.
    posts = [raw[0] for raw in result.all()]    
    
    posts_data = []
    for post in posts:
        posts_data.append({
            "id":str(post.id),
            "captiopn":post.caption,
            "url":post.url,
            "file_type":post.file_type,
            "file_name":post.file_name,
            "created_at":post.date.isoformat()
        })
    
    return {"posts": posts_data}

