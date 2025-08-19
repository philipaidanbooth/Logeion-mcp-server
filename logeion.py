from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP
import sqlite3
import spacy
import logging
import os
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("logeion")

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(SCRIPT_DIR, "dvlg-wheel-mini.sqlite")

# Load spaCy model once at module level
try:
    nlp = spacy.load("la_core_web_lg")
    logger.info("LatinCy model loaded successfully!")
except OSError:
    logger.warning("Warning: LatinCy model not found. Please install it with: python -m spacy download la_core_web_lg")
    nlp = None

# Pydantic models for better schema documentation
class WordSearchResult(BaseModel):
    success: bool = Field(description="Whether the search was successful")
    word: str = Field(description="The original search term")
    lemma: Optional[str] = Field(description="The lemmatized form if found", default=None)
    results: Optional[List[Any]] = Field(description="Database results if found", default=None)
    method: str = Field(description="How the search was performed: exact_match, lemmatized, none, or error")
    error: Optional[str] = Field(description="Error message if something went wrong", default=None)

class ServerInfo(BaseModel):
    name: str = Field(description="Server name")
    version: str = Field(description="Server version")
    description: str = Field(description="Server description")
    tools_available: List[str] = Field(description="List of available tools")
    database_status: str = Field(description="Database connection status")
    spacy_status: str = Field(description="spaCy model status")

@mcp.tool()
def get_word(word: str) -> WordSearchResult:
    """
    Search for a Latin word in the dictionary database.
    
    This tool searches for Latin words and automatically attempts lemmatization
    if the exact word is not found. It connects to a SQLite database containing
    Latin dictionary entries.
    
    Args:
        word: The Latin word to search for (e.g., "amare", "amo", "amamus")
        
    Returns:
        A structured result containing the search outcome, including the original
        word, any lemmatized form found, database results, and search method used.
        
    Example:
        Search for "amo" (I love) will find the lemma "amare" and return
        dictionary entries for the verb "to love".
    """
    try: 
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            # First try to find the word as-is
            cursor.execute("SELECT * FROM Entries WHERE head = ?", (word,))
            results = cursor.fetchall()
            
            if results:
                return WordSearchResult(
                    success=True,
                    word=word,
                    results=results,
                    method="exact_match"
                )
            
            # If no results and spaCy is available, try lemmatization
            if nlp is not None:
                doc = nlp(word)
                if len(doc) > 0:
                    lemma = doc[0].lemma_
                    
                    cursor.execute("SELECT * FROM Entries WHERE head = ?", (lemma,))
                    results = cursor.fetchall()
                    
                    if results:
                        return WordSearchResult(
                            success=True,
                            word=word,
                            lemma=lemma,
                            results=results,
                            method="lemmatized"
                        )
            
            return WordSearchResult(
                success=False,
                word=word,
                error=f"No results found for '{word}' or its lemma",
                method="none"
            )
            
        finally:
            conn.close()  # Always closes, even if error
    
    except Exception as e:
        logger.error(f"Error searching for word '{word}': {str(e)}")
        return WordSearchResult(
            success=False,
            word=word,
            error=str(e),
            method="error"
        )

@mcp.tool()
def get_server_info() -> ServerInfo:
    """
    Get information about the Logeion MCP server.
    
    This tool provides metadata about the server, including its capabilities,
    current status, and available tools. Useful for server inspection and
    health checking.
    
    Returns:
        Server information including name, version, description, available tools,
        database status, and spaCy model status.
    """
    # Check database status
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check spaCy status
    if nlp is not None:
        spacy_status = "loaded (la_core_web_lg)"
    else:
        spacy_status = "not available"
    
    return ServerInfo(
        name="Logeion MCP Server",
        version="1.0.0",
        description="A powerful Latin dictionary MCP server with lemmatization support",
        tools_available=["get_word", "get_server_info", "explore_database"],
        database_status=db_status,
        spacy_status=spacy_status
    )

@mcp.tool()
def explore_database(table_name: str = "Entries", limit: int = 10) -> Dict[str, Any]:
    """
    Explore the database structure and sample data.
    
    This tool allows inspection of the database schema and provides sample
    data for understanding the available information. Useful for development
    and debugging.
    
    Args:
        table_name: The table to explore (default: "Entries")
        limit: Maximum number of sample rows to return (default: 10)
        
    Returns:
        Database schema information and sample data.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema = cursor.fetchall()
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
            sample_data = cursor.fetchall()
            
            # Get column names
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []
            
            return {
                "success": True,
                "table": table_name,
                "schema": schema,
                "column_names": column_names,
                "sample_data": sample_data,
                "total_rows": len(sample_data)
            }
            
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error exploring database: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "table": table_name
        }

if __name__ == "__main__":
    logger.info("Starting Logeion MCP Server...")
    logger.info(f"Database path: {DATABASE_PATH}")
    logger.info(f"spaCy model loaded: {nlp is not None}")
    mcp.run(transport='stdio')

