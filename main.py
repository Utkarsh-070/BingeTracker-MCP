from fastmcp import FastMCP
import os
import json
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "binge.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("BingeTracker")

# Load categories at startup
def load_categories():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

CATEGORIES = load_categories()

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS shows(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL,
                genre TEXT DEFAULT 'other',
                status TEXT DEFAULT 'Plan to Watch',
                season INTEGER DEFAULT 1,
                episode INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                last_updated TEXT
            )
        """)
        # Migrate existing DBs: add genre column if missing
        try:
            c.execute("ALTER TABLE shows ADD COLUMN genre TEXT DEFAULT 'other'")
        except sqlite3.OperationalError:
            pass  # Column already exists

init_db()

@mcp.tool()
def get_genres(media_type: str):
    """Get valid genres for a media type. Use this to see what genres are available before adding a show."""
    valid_types = list(CATEGORIES.keys())
    if media_type not in valid_types:
        return f"Unknown media type '{media_type}'. Valid types: {valid_types}"
    return {"media_type": media_type, "genres": CATEGORIES[media_type]}

@mcp.tool()
def add_show(title: str, show_type: str, genre: str = "other", status: str = "Plan to Watch"):
    """Add a show to your binge list. Use get_genres first to see valid types and genres."""
    title = title.title()
    valid_types = list(CATEGORIES.keys())
    if show_type not in valid_types:
        return f"Bro, '{show_type}' ain't a valid type. Use: {valid_types}"

    valid_genres = CATEGORIES[show_type]
    if genre not in valid_genres:
        return f"'{genre}' isn't a valid genre for {show_type}. Pick from: {valid_genres}"

    valid_statuses = ["Watching", "Completed", "Plan to Watch", "Dropped"]
    if status not in valid_statuses:
        return f"Bro, '{status}' ain't a real status. Use: {valid_statuses}"

    try:
        with sqlite3.connect(DB_PATH) as c:
            cur = c.execute(
                "INSERT INTO shows(title, type, genre, status, last_updated) VALUES (?,?,?,?,?)",
                (title, show_type, genre, status, datetime.now().isoformat())
            )
            return {"status": "Added", "id": cur.lastrowid, "msg": f"Added {title} [{show_type}/{genre}]. Time to binge."}
    except sqlite3.IntegrityError:
        return f"Yo, you already added '{title}'. Update it instead."

@mcp.tool()
def update_progress(title: str, season: int, episode: int, status: str = "Watching"):
    title = title.title()
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
    title = title.title()
    if not (0 <= rating <= 10):
        return "Rating must be 0-10. Don't be extra."

    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("SELECT id FROM shows WHERE title = ?", (title,))
        if not cur.fetchone():
            return f"Bro, '{title}' isn't in your list. Add it first."
        c.execute("UPDATE shows SET rating = ? WHERE title = ?", (rating, title))
        return f"Rated {title} a {rating}/10."

@mcp.tool()
def my_list(status: str = None, genre: str = None, media_type: str = None):
    """View your binge list. Optionally filter by status, genre, or media type."""
    with sqlite3.connect(DB_PATH) as c:
        query = "SELECT title, type, genre, status, season, episode, rating FROM shows"
        conditions = []
        params = []
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        if genre:
            conditions.append("genre = ?")
            params.append(genre)
        if media_type:
            conditions.append("type = ?")
            params.append(media_type)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
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
    mcp.run(transport="streamable-http")