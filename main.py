from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

app = FastAPI()

# origins = ["http://localhost:5173"]
origins = ["https://b7-9414.github.io"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Idea(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    category: str
    likes: Optional[int] = 0

class Comment(BaseModel):
    idea_id: int
    text: str

def get_db_connection():
    conn = sqlite3.connect("ideas.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def startup():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            category TEXT,
            likes INTEGER DEFAULT 0
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER,
            text TEXT,
            FOREIGN KEY(idea_id) REFERENCES ideas(id)
        )
    ''')
    # Add the missing likes table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER,
            user_id TEXT,
            FOREIGN KEY(idea_id) REFERENCES ideas(id),
            UNIQUE(idea_id, user_id)
        )
    ''')
    conn.commit()
    conn.close()

@app.get("/ideas")
def read_ideas():
    conn = get_db_connection()
    ideas_raw = conn.execute("SELECT * FROM ideas").fetchall()
    ideas = []
    for row in ideas_raw:
        idea = dict(row)
        # Count comments for this idea
        comment_count = conn.execute(
            "SELECT COUNT(*) FROM comments WHERE idea_id = ?", (idea["id"],)
        ).fetchone()[0]
        idea["comments_count"] = comment_count
        ideas.append(idea)
    conn.close()
    return ideas

@app.post("/ideas")
def create_idea(idea: Idea):
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO ideas (title, description, category, likes) VALUES (?, ?, ?, ?)",
        (idea.title, idea.description, idea.category, idea.likes or 0),
    )
    conn.commit()
    idea_id = cursor.lastrowid
    conn.close()
    return {"message": "Idea added", "id": idea_id}

@app.put("/ideas/{idea_id}")
def update_idea(idea_id: int, idea: Idea):
    conn = get_db_connection()
    result = conn.execute(
        "UPDATE ideas SET title = ?, description = ?, category = ?, likes = ? WHERE id = ?",
        (idea.title, idea.description, idea.category, idea.likes, idea_id),
    )
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"message": "Idea updated"}

@app.delete("/ideas/{idea_id}")
def delete_idea(idea_id: int):
    conn = get_db_connection()
    result = conn.execute("DELETE FROM ideas WHERE id = ?", (idea_id,))
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"message": "Idea deleted"}

from fastapi import Query

@app.post("/ideas/{idea_id}/like")
def toggle_like(idea_id: int, user_id: str = Query(...)):
    conn = get_db_connection()
    
    # Check if the idea exists
    idea_exists = conn.execute("SELECT 1 FROM ideas WHERE id = ?", (idea_id,)).fetchone()
    if not idea_exists:
        conn.close()
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Check if user already liked this idea
    exists = conn.execute("SELECT 1 FROM likes WHERE idea_id = ? AND user_id = ?", (idea_id, user_id)).fetchone()

    if exists:
        # Remove like
        conn.execute("DELETE FROM likes WHERE idea_id = ? AND user_id = ?", (idea_id, user_id))
        conn.execute("UPDATE ideas SET likes = likes - 1 WHERE id = ?", (idea_id,))
        liked = False
    else:
        # Add like
        conn.execute("INSERT INTO likes (idea_id, user_id) VALUES (?, ?)", (idea_id, user_id))
        conn.execute("UPDATE ideas SET likes = likes + 1 WHERE id = ?", (idea_id,))
        liked = True

    conn.commit()
    conn.close()
    return {"liked": liked}

@app.get("/ideas/{idea_id}/comments", response_model=List[Comment])
def get_comments(idea_id: int):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT idea_id, text FROM comments WHERE idea_id = ?", (idea_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/comments")
def post_comment(comment: Comment):
    conn = get_db_connection()
    
    # Check if the idea exists
    idea_exists = conn.execute("SELECT 1 FROM ideas WHERE id = ?", (comment.idea_id,)).fetchone()
    if not idea_exists:
        conn.close()
        raise HTTPException(status_code=404, detail="Idea not found")
    
    conn.execute(
        "INSERT INTO comments (idea_id, text) VALUES (?, ?)",
        (comment.idea_id, comment.text),
    )
    conn.commit()
    conn.close()
    return {"message": "Comment added"}