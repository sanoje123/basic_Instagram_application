from fastapi import FastAPI, HTTPException, Form, Depends, File, UploadFile
from .schema import PostCreate, PostResponse
from app.db import create_db_and_tables, get_async_session, Post
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
import shutil
import os
import uuid
import tempfile

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
    temp_file_path = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        with open(temp_file_path, 'rb') as f:
            upload_resut = imagekit.files.upload(
                file=f,
                file_name=file.filename,
                use_unique_file_name=True,
                tags=["backend-upload"]
            )
            
        post = Post(
                caption=caption,
                url=upload_resut.url,
                file_type="video" if file.content_type.startswith("video/") else "image",
                file_name=upload_resut.name
            )
        session.add(post)   #This tells SQLAlchemy:"Add this object to the transaction." - It does NOT write to database yet.
        await session.commit()  #Now SQLAlchemy sends the query to the database. Equivalent SQL: INSERT INTO post (...) VALUES (...)
        await session.refresh(post) #After commit, the post object is updated with any new data from the database, such as the generated id. This is important for getting the id of the newly created post.
        return post 
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        await file.close()

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
            "caption":post.caption,
            "url":post.url,
            "file_type":post.file_type,
            "file_name":post.file_name,
            "created_at":post.date.isoformat()
        })
    
    return {"posts": posts_data}


@app.delete("/post/{post_id}")
async def delete_post(post_id: str, session:AsyncSession = Depends(get_async_session)):
    try:
        post_uuid = uuid.UUID(post_id)
        
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first() #The query result is a SQLAlchemy result object, not yet the Post instance directly. scalars() - This extracts the ORM model objects from the result. Without it, the returned rows may be wrapped in row tuples. first() - This takes the first matching result, or None if nothing was found.
        
        if not post:
            raise HTTPException(status_code=404, detail="Element not found.")
        
        await session.delete(post)
        await session.commit()
        
        return {"success":True, "message": "Post deleted successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


