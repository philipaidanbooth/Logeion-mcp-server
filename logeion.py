from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import sqlite3
import spacy
import logging
import os

mcp = FastMCP("logeion")

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(SCRIPT_DIR, "dvlg-wheel-mini.sqlite")

# Load spaCy model once at module level
try:
    nlp = spacy.load("la_core_web_lg")
    logging.info("LatinCy model loaded successfully!")
except OSError:
    logging.warning("Warning: LatinCy model not found. Please install it with: python -m spacy download la_core_web_lg")
    nlp = None


@mcp.tool()
def get_word(word):
    try: 
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            # First try to find the word as-is
            cursor.execute("SELECT * FROM Entries WHERE head = ?", (word,))
            results = cursor.fetchall()
            
            if results:
                return {
                    "success": True,
                    "word": word,
                    "results": results,
                    "method": "exact_match"
                }
            
            # If no results and spaCy is available, try lemmatization
            if nlp is not None:
                lemma = nlp(word)[0].lemma_
                
                cursor.execute("SELECT * FROM Entries WHERE head = ?", (lemma,))
                results = cursor.fetchall()
                
                if results:
                    return {
                        "success": True,
                        "word": word,
                        "lemma": lemma,
                        "results": results,
                        "method": "lemmatized"
                    }
            return {
                "success": False,
                "word": word,
                "error": f"No results found for '{word}' or its lemma",
                "method": "none"
            }
            
        finally:
            conn.close()  # Always closes, even if error
    
    except Exception as e:
        return {
            "success": False,
            "word": word,
            "error": str(e),
            "method": "error"
        }
            


if __name__ == "__main__":
    mcp.run(transport='stdio')

