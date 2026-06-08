#Campuspulse code
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime

# ── App Initialisation ──────────────────────────────────────────────────────
app = FastAPI(
    title="CampusPulse",
    description="A Student Notice Board API",
    version="1.0.0"
)

DATABASE = "campuspulse.db"

# ── Database Setup ───────────────────────────────────────────────────────────
def init_db():
    """Create the notices table if it does not already exist."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT    NOT NULL,
            message    TEXT    NOT NULL,
            author     TEXT    NOT NULL,
            created_at TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()   # Run once when the server starts

# ── Data Models ──────────────────────────────────────────────────────────────
class NoticeIn(BaseModel):
    """Input model — what the client sends."""
    title:   str
    message: str
    author:  str

class NoticeOut(BaseModel):
    """Output model — what the server returns."""
    id:         int
    title:      str
    message:    str
    author:     str
    created_at: str

# ── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {"status": "ok", "app": "CampusPulse"}

@app.get("/notices", response_model=List[NoticeOut], tags=["Notices"])
def get_all_notices():
    """Return all notices, newest first."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, message, author, created_at FROM notices ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "title": r[1], "message": r[2], "author": r[3], "created_at": r[4]}
        for r in rows
    ]

@app.post("/notices", tags=["Notices"])
def create_notice(notice: NoticeIn):
    """Create a new notice."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notices (title, message, author, created_at) VALUES (?, ?, ?, ?)",
        (notice.title, notice.message, notice.author, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "message": "Notice created successfully"}

@app.delete("/notices/{notice_id}", tags=["Notices"])
def delete_notice(notice_id: int):
    """Delete a notice by ID."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM notices WHERE id = ?", (notice_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Notice {notice_id} not found")
    cursor.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
    conn.commit()
    conn.close()
    return {"message": f"Notice {notice_id} deleted"}
