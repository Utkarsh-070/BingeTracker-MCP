from fastmcp import FastMCP
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "binge.db")

mcp = FastMCP("BingeTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS shows(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL,  -- 'Anime', 'Series', 'Movie'
                status TEXT DEFAULT 'Plan to Watch', -- 'Watching', 'Completed', 'Dropped'
                season INTEGER DEFAULT 1,
                episode INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                last_updated TEXT
            )
        """)

init_db()

@mcp.tool()
def add_show(title: str, type: str, status: str = "Plan to Watch"):
    valid_statuses = ["Watching", "Completed", "Plan to Watch", "Dropped"]
    if status not in valid_statuses:
        return f"Bro, '{status}' ain't a real status. Use: {valid_statuses}"

    try:
        with sqlite3.connect(DB_PATH) as c:
            cur = c.execute(
                "INSERT INTO shows(title, type, status, last_updated) VALUES (?,?,?,?)",
                (title, type, status, datetime.now().isoformat())
            )
            return {"status": "Added", "id": cur.lastrowid, "msg": f"Added {title}. Time to binge."}
    except sqlite3.IntegrityError:
        return f"Yo, you already added '{title}'. Update it instead."

@mcp.tool()
def update_progress(title: str, season: int, episode: int, status: str = "Watching"):

    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("SELECT id FROM shows WHERE title = ?", (title,))
        if not cur.fetchone():
            return f"Bro, you aren't tracking '{title}' yet. Add it first."

        c.execute(
            """
            UPDATE shows 
            SET season = ?, episode = ?, status = ?, last_updated = ? 
            WHERE title = ?
            """,
            (season, episode, status, datetime.now().isoformat(), title)
        )
        return f"Updated {title} to S{season} E{episode}. Keep grinding."

@mcp.tool()
def rate_show(title: str, rating: float):
    if not (0 <= rating <= 10):
        return "Rating must be 0-10. Don't be extra."

    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("SELECT id FROM shows WHERE title = ?", (title,))
        if not cur.fetchone():
            return f"Bro, '{title}' isn't in your list. Add it first."
        c.execute("UPDATE shows SET rating = ? WHERE title = ?", (rating, title))
        return f"Rated {title} a {rating}/10. Taste established."

@mcp.tool()
def my_list(status: str = None):
    with sqlite3.connect(DB_PATH) as c:
        query = "SELECT title, type, status, season, episode, rating FROM shows"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        query += " ORDER BY last_updated DESC"
        
        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, r)) for r in cur.fetchall()]
        
        if not results:
            return "Your list is empty, bro. Go touch grass or add some shows."
            
        return results

@mcp.resource("binge://categories", mime_type="application/json")
def categories():
    CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")
    if not os.path.exists(CATEGORIES_PATH):
         return '{"error": "File not found, bro"}'
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    # transport="streamable-http" makes this a proper remote MCP server
    # It will serve at http://localhost:8000/mcp by default
    mcp.run(transport="streamable-http")