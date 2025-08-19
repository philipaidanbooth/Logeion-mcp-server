#!/usr/bin/env python3
"""
Comprehensive test suite for the Logeion MCP Server.

This test suite covers:
- Tool functionality
- Database connectivity
- Error handling
- Schema validation
- Performance testing
"""

import unittest
import sqlite3
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
import json

# Add the current directory to the path so we can import logeion
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logeion import get_word, get_server_info, explore_database, WordSearchResult, ServerInfo

class TestLogeionMCPServer(unittest.TestCase):
    """Test cases for the Logeion MCP Server."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite')
        self.temp_db.close()
        
        # Create test database with sample data
        self.create_test_database()
        
        # Store original database path
        self.original_db_path = None
        if hasattr(sys.modules['logeion'], 'DATABASE_PATH'):
            self.original_db_path = sys.modules['logeion'].DATABASE_PATH
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original database path
        if self.original_db_path:
            sys.modules['logeion'].DATABASE_PATH = self.original_db_path
        
        # Remove temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def create_test_database(self):
        """Create a test database with sample Latin words."""
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Create Entries table
        cursor.execute('''
            CREATE TABLE Entries (
                id INTEGER PRIMARY KEY,
                head TEXT NOT NULL,
                definition TEXT,
                part_of_speech TEXT,
                etymology TEXT
            )
        ''')
        
        # Insert sample data
        sample_data = [
            ('amare', 'to love', 'verb', 'from Proto-Indo-European *am-'),
            ('amo', 'I love', 'verb', 'first person singular present of amare'),
            ('amamus', 'we love', 'verb', 'first person plural present of amare'),
            ('puer', 'boy', 'noun', 'from Proto-Indo-European *ph₂wḗr'),
            ('puella', 'girl', 'noun', 'diminutive of puer'),
            ('bonus', 'good', 'adjective', 'from Proto-Indo-European *dʰew-'),
            ('magna', 'great', 'adjective', 'feminine singular of magnus')
        ]
        
        cursor.executemany(
            'INSERT INTO Entries (head, definition, part_of_speech, etymology) VALUES (?, ?, ?, ?)',
            sample_data
        )
        
        conn.commit()
        conn.close()
    
    def test_get_word_exact_match(self):
        """Test exact word matching."""
        # Temporarily set the database path to our test database
        sys.modules['logeion'].DATABASE_PATH = self.temp_db.name
        
        result = get_word("amare")
        
        self.assertIsInstance(result, WordSearchResult)
        self.assertTrue(result.success)
        self.assertEqual(result.word, "amare")
        self.assertEqual(result.method, "exact_match")
        self.assertIsNotNone(result.results)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0][1], "amare")  # head column
    
    def test_get_word_lemmatization(self):
        """Test word lemmatization when exact match not found."""
        # Temporarily set the database path to our test database
        sys.modules['logeion'].DATABASE_PATH = self.temp_db.name
        
        # Mock spaCy to return a known lemma
        with patch('logeion.nlp') as mock_nlp:
            mock_doc = MagicMock()
            mock_doc.__getitem__.return_value.lemma_ = "amare"
            mock_doc.__len__.return_value = 1
            mock_nlp.return_value = mock_doc
            
            result = get_word("amo")
            
            self.assertIsInstance(result, WordSearchResult)
            self.assertTrue(result.success)
            self.assertEqual(result.word, "amo")
            self.assertEqual(result.lemma, "amare")
            self.assertEqual(result.method, "lemmatized")
            self.assertIsNotNone(result.results)
    
    def test_get_word_no_results(self):
        """Test behavior when no results are found."""
        # Temporarily set the database path to our test database
        sys.modules['logeion'].DATABASE_PATH = self.temp_db.name
        
        result = get_word("nonexistentword")
        
        self.assertIsInstance(result, WordSearchResult)
        self.assertFalse(result.success)
        self.assertEqual(result.word, "nonexistentword")
        self.assertEqual(result.method, "none")
        self.assertIsNotNone(result.error)
    
    def test_get_word_database_error(self):
        """Test error handling when database operations fail."""
        # Set an invalid database path
        sys.modules['logeion'].DATABASE_PATH = "/invalid/path/database.sqlite"
        
        result = get_word("test")
        
        self.assertIsInstance(result, WordSearchResult)
        self.assertFalse(result.success)
        self.assertEqual(result.method, "error")
        self.assertIsNotNone(result.error)
    
    def test_get_server_info(self):
        """Test server information retrieval."""
        # Temporarily set the database path to our test database
        sys.modules['logeion'].DATABASE_PATH = self.temp_db.name
        
        result = get_server_info()
        
        self.assertIsInstance(result, ServerInfo)
        self.assertEqual(result.name, "Logeion MCP Server")
        self.assertEqual(result.version, "1.0.0")
        self.assertIn("get_word", result.tools_available)
        self.assertIn("get_server_info", result.tools_available)
        self.assertIn("explore_database", result.tools_available)
        self.assertEqual(result.database_status, "connected")
    
    def test_explore_database(self):
        """Test database exploration functionality."""
        # Temporarily set the database path to our test database
        sys.modules['logeion'].DATABASE_PATH = self.temp_db.name
        
        result = explore_database("Entries", 5)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["table"], "Entries")
        self.assertIsNotNone(result["schema"])
        self.assertIsNotNone(result["column_names"])
        self.assertIsNotNone(result["sample_data"])
        self.assertLessEqual(result["total_rows"], 5)
    
    def test_explore_database_invalid_table(self):
        """Test database exploration with invalid table name."""
        # Temporarily set the database path to our test database
        sys.modules['logeion'].DATABASE_PATH = self.temp_db.name
        
        result = explore_database("InvalidTable")
        
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
    
    def test_word_search_result_schema(self):
        """Test that WordSearchResult follows the expected schema."""
        result = WordSearchResult(
            success=True,
            word="test",
            method="exact_match"
        )
        
        # Test that the result can be serialized to JSON
        json_str = result.model_dump_json()
        parsed = json.loads(json_str)
        
        self.assertIn("success", parsed)
        self.assertIn("word", parsed)
        self.assertIn("method", parsed)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["word"], "test")
        self.assertEqual(parsed["method"], "exact_match")
    
    def test_server_info_schema(self):
        """Test that ServerInfo follows the expected schema."""
        result = ServerInfo(
            name="Test Server",
            version="1.0.0",
            description="Test description",
            tools_available=["tool1", "tool2"],
            database_status="connected",
            spacy_status="loaded"
        )
        
        # Test that the result can be serialized to JSON
        json_str = result.model_dump_json()
        parsed = json.loads(json_str)
        
        self.assertIn("name", parsed)
        self.assertIn("version", parsed)
        self.assertIn("description", parsed)
        self.assertIn("tools_available", parsed)
        self.assertIn("database_status", parsed)
        self.assertIn("spacy_status", parsed)
        
        self.assertEqual(parsed["name"], "Test Server")
        self.assertEqual(parsed["version"], "1.0.0")
        self.assertEqual(parsed["tools_available"], ["tool1", "tool2"])

class TestPerformance(unittest.TestCase):
    """Performance tests for the MCP server."""
    
    def test_database_connection_performance(self):
        """Test database connection performance."""
        import time
        
        start_time = time.time()
        
        # Create a temporary database
        with tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite') as temp_db:
            temp_db.close()
            
            try:
                conn = sqlite3.connect(temp_db.name)
                cursor = conn.cursor()
                
                # Create a simple table
                cursor.execute('CREATE TABLE test (id INTEGER, value TEXT)')
                
                # Insert some test data
                for i in range(1000):
                    cursor.execute('INSERT INTO test VALUES (?, ?)', (i, f'value_{i}'))
                
                conn.commit()
                conn.close()
                
                # Test query performance
                conn = sqlite3.connect(temp_db.name)
                cursor = conn.cursor()
                
                start_query = time.time()
                cursor.execute('SELECT * FROM test WHERE id = ?', (500,))
                result = cursor.fetchone()
                query_time = time.time() - start_query
                
                conn.close()
                
                # Query should complete in under 100ms
                self.assertLess(query_time, 0.1)
                self.assertIsNotNone(result)
                
            finally:
                if os.path.exists(temp_db.name):
                    os.unlink(temp_db.name)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
