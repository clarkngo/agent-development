"""Simple movie chat/search/recommender agent.

This module exposes two small tools usable by a root agent:
- `search_movies(query, max_results=5)` — fuzzy search on title and synopsis.
- `recommend_similar(title, max_results=5)` — recommend movies that share genres.

The implementation uses a tiny in-memory movie list so this is runnable without external APIs.
"""

from typing import List, Dict
try:
    from google.adk.agents import Agent
except Exception:
    # Local fallback so the module remains importable during development when
    # the real google.adk package isn't available.
    from dataclasses import dataclass, field

    @dataclass
    class Agent:
        name: str
        model: str = ""
        description: str = ""
        instruction: str = ""
        tools: list = field(default_factory=list)

# Small sample in-memory movie database
MOVIES: List[Dict] = [
    {
        "title": "Inception",
        "year": 2010,
        "genres": ["Sci-Fi", "Thriller"],
        "synopsis": "A thief who steals corporate secrets through dream-sharing technology."
    },
    {
        "title": "The Matrix",
        "year": 1999,
        "genres": ["Sci-Fi", "Action"],
        "synopsis": "A computer hacker learns about the true nature of his reality."
    },
    {
        "title": "Interstellar",
        "year": 2014,
        "genres": ["Sci-Fi", "Drama"],
        "synopsis": "A team travels through a wormhole to ensure humanity's survival."
    },
    {
        "title": "Toy Story",
        "year": 1995,
        "genres": ["Animation", "Family", "Comedy"],
        "synopsis": "Toys come to life when humans aren't around."
    },
    {
        "title": "The Shawshank Redemption",
        "year": 1994,
        "genres": ["Drama"],
        "synopsis": "Two imprisoned men bond over years, finding solace and eventual redemption."
    }
]


def search_movies(query: str, max_results: int = 5) -> dict:
    """Search for movies by title or synopsis (case-insensitive).

    Returns a dict with 'status' and 'results' (list of movie dicts).
    """
    q = (query or "").strip().lower()
    if not q:
        return {"status": "error", "error_message": "Empty query provided."}

    matches = []
    for m in MOVIES:
        if q in m["title"].lower() or q in m["synopsis"].lower():
            matches.append({
                "title": m["title"],
                "year": m["year"],
                "genres": m["genres"],
                "synopsis": m["synopsis"]
            })
    # If nothing matched by text, do a fuzzy-ish genre match (query equals a genre)
    if not matches:
        for m in MOVIES:
            if q.title() in m["genres"]:
                matches.append({
                    "title": m["title"],
                    "year": m["year"],
                    "genres": m["genres"],
                    "synopsis": m["synopsis"]
                })

    return {"status": "success", "results": matches[:max_results]}


def recommend_similar(title: str, max_results: int = 5) -> dict:
    """Recommend movies similar to `title` based on overlapping genres.

    Returns a dict with 'status' and 'results' (list of movie dicts).
    """
    if not title:
        return {"status": "error", "error_message": "Empty title provided."}

    # Find the movie (case-insensitive exact match on title)
    target = None
    for m in MOVIES:
        if m["title"].lower() == title.strip().lower():
            target = m
            break

    if target is None:
        return {"status": "error", "error_message": f"Movie titled '{title}' not found."}

    # Score other movies by shared genres
    scores = []
    target_genres = set(target["genres"])
    for m in MOVIES:
        if m["title"] == target["title"]:
            continue
        shared = target_genres.intersection(set(m["genres"]))
        score = len(shared)
        if score > 0:
            scores.append((score, m))

    # Sort by score desc then year desc
    scores.sort(key=lambda x: (x[0], x[1]["year"]), reverse=True)
    results = []
    for _, m in scores[:max_results]:
        results.append({
            "title": m["title"],
            "year": m["year"],
            "genres": m["genres"],
            "synopsis": m["synopsis"]
        })

    return {"status": "success", "results": results}


# Define the root agent
root_agent = Agent(
    name="movie_recommender_agent",
    model="gemini-2.0-flash",
    description="A simple movie search and recommendation agent.",
    instruction=(
        "Use the provided tools to search for movies and to recommend similar movies. "
        "Tools: search_movies(query), recommend_similar(title)."
    ),
    tools=[search_movies, recommend_similar]
)