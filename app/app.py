from fastapi import FastAPI, HTTPException
from .schema import PostCreate, PostResponse

app = FastAPI()

text_psots = {
    1: { "title": "Introduction to Python", "content": "Python is a high-level, dynamically typed programming language known for its readability and versatility." },
    2: { "title": "Machine Learning Basics", "content": "Machine learning is a field of artificial intelligence that focuses on building systems that learn from data." },
    3: { "title": "REST APIs Explained", "content": "A REST API allows communication between client and server using standard HTTP methods like GET, POST, PUT, and DELETE." },
    4: { "title": "Database Indexing", "content": "Indexing improves database query performance by allowing faster lookup of rows in a table." },
    5: { "title": "Docker Containers", "content": "Docker enables developers to package applications and their dependencies into portable containers." },
    6: { "title": "Neural Networks", "content": "Neural networks are computational models inspired by the human brain, commonly used in deep learning." },
    7: { "title": "Git Version Control", "content": "Git is a distributed version control system used to track changes in source code during development." },
    8: { "title": "Cloud Computing", "content": "Cloud computing provides on-demand access to computing resources over the internet." },
    9: { "title": "Data Structures", "content": "Data structures organize and store data efficiently, examples include arrays, linked lists, and trees." },
    10: { "title": "Cybersecurity Fundamentals", "content": "Cybersecurity involves protecting systems, networks, and data from digital attacks." }

}

@app.get("/posts")
def get_all_posts(limit: int = None):
    if limit:
        return list(text_psots.values())[:limit]
    return text_psots

@app.get("/posts/{post_id}")
def get_post(post_id: int) -> PostResponse:
    if post_id not in text_psots:
        raise HTTPException(status_code=404, detail="Post not found")
    return text_psots.get(post_id)

@app.post("/posts")
def add_post(post:PostCreate) -> PostResponse:
    new_post = {"title":post.title, "content":post.content}
    text_psots[max(text_psots.keys())+1] = new_post
    return new_post