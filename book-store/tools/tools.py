
from google.adk.tools import tool
from .engine import SHARED_KB

def search_club_book(query: str) -> str:
    """
    Searches the collection of active markdown books in the store.
    Use this to retrieve exact passages, thematic context, or plot details.
    """
    return SHARED_KB.query(query)
