#  BingeTracker MCP

A remote **Model Context Protocol (MCP)** server that lets AI assistants manage your personal watchlist — track shows, movies, anime, and more through natural conversation.

Built with [FastMCP](https://github.com/jlowin/fastmcp) and SQLite.

---

## What It Does

BingeTracker exposes a set of tools over MCP that any compatible AI client (Claude, Cursor, etc.) can call to:

- **Add** shows, movies, anime, or documentaries to your list
- **Update** watch progress (season & episode)
- **Rate** anything on a 0–10 scale
- **View & filter** your list by status, genre, or media type
- **Browse genres** for each media category

All data is stored locally in a SQLite database that gets created automatically on first run.

---

## Available Tools

| Tool | Description |
|------|-------------|
| `get_genres` | List valid genres for a given media type |
| `add_show` | Add a new title to your watchlist |
| `update_progress` | Update season/episode and status |
| `rate_show` | Rate a title from 0 to 10 |
| `my_list` | View your full list with optional filters |

### Resource

| URI | Description |
|-----|-------------|
| `binge://categories` | Returns the full genre taxonomy as JSON |

---

## Supported Categories

| Media Type | Genres |
|------------|--------|
| **Anime** | shonen, seinen, shojo, isekai, mecha, slice_of_life, sports, psychological_thriller, romance, cyberpunk, classic_90s, movie_adaptation |
| **TV Series** | sci_fi_fantasy, crime_mystery, sitcom_comedy, k_drama, historical_drama, tech_dystopia, horror_supernatural, action_adventure, political_drama, reality_trash, limited_series |
| **Movies** | blockbuster_action, sci_fi, horror_slasher, psychological_horror, rom_com, indie_arthouse, biopic, war_history, mystery_noir, animated_feature, mcu_dc_superhero |
| **Western Animation** | adult_animation, superhero_animated, sci_fi_animated, childhood_nostalgia, experimental |
| **Documentary** | tech_coding, true_crime, nature_science, history, finance_business, biographical, sports_doc |
| **Web Content** | tech_tutorials, video_essays, gaming_stream_vods, devlogs, podcast_video, retention_editing_guides, short_films |

---

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

```bash
git clone https://github.com/Utkarsh-070/BingeTracker-MCP.git
cd BingeTracker-MCP
```

**Using uv:**
```bash
uv sync
```

**Using pip:**
```bash
pip install fastmcp
```

### Run the Server

```bash
python main.py
```

The server starts on `http://localhost:8000` using the Streamable HTTP transport. The SQLite database (`binge.db`) is created automatically on first run.

---

## Connect to an MCP Client

### Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "BingeTracker": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Cursor

Add to your MCP settings:

```json
{
  "mcpServers": {
    "BingeTracker": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Once connected, just talk naturally — *"Add Attack on Titan as anime, genre shonen"* or *"What's on my list?"*

---

## Project Structure

```
BingeTracker-MCP/
├── main.py              # MCP server with all tools and resources
├── categories.json      # Genre taxonomy for all media types
├── pyproject.toml       # Project metadata and dependencies
├── uv.lock              # Dependency lock file
└── README.md
```

---

## License

[MIT](LICENSE)
