from google.adk.tools import tool

from ..engine import SHARED_KB

@tool
def search_shared_bookstore(query: str) -> str:
    """
    Queries the central book-store repository for explicit text data.
    Use this tool to find direct quotes, plot context, or contextual character facts
    from active club reading materials like Romeo and Juliet or Dracula.
    """
    return SHARED_KB.similarity_search(query=query, top_k=3)
