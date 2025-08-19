#!/usr/bin/env python3
"""
Demo script for the Logeion MCP Server.

This script demonstrates the capabilities of the MCP server by running
various examples and showing the results.
"""

import json
import sys
import os

# Add the current directory to the path so we can import logeion
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_result(tool_name, input_data, result):
    """Print a formatted result."""
    print(f"\n🔧 Tool: {tool_name}")
    print(f"📥 Input: {json.dumps(input_data, indent=2)}")
    print(f"📤 Output:")
    print(json.dumps(result, indent=2, default=str))

def demo_server_info():
    """Demonstrate the get_server_info tool."""
    print_header("Server Information Demo")
    
    try:
        from logeion import get_server_info
        result = get_server_info()
        print_result("get_server_info", {}, result)
        
        print(f"\n✅ Server Status: {result.database_status}")
        print(f"🔤 spaCy Model: {result.spacy_status}")
        print(f"🛠️  Available Tools: {', '.join(result.tools_available)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_word_search():
    """Demonstrate the get_word tool with various examples."""
    print_header("Word Search Demo")
    
    try:
        from logeion import get_word
        
        # Example 1: Exact match
        print("\n📚 Example 1: Exact word match")
        result = get_word("amare")
        print_result("get_word", {"word": "amare"}, result)
        
        # Example 2: Lemmatization
        print("\n📚 Example 2: Lemmatization (finding base form)")
        result = get_word("amo")
        print_result("get_word", {"word": "amo"}, result)
        
        # Example 3: No results
        print("\n📚 Example 3: Word not found")
        result = get_word("nonexistentword")
        print_result("get_word", {"word": "nonexistentword"}, result)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_database_exploration():
    """Demonstrate the explore_database tool."""
    print_header("Database Exploration Demo")
    
    try:
        from logeion import explore_database
        
        result = explore_database("Entries", 3)
        print_result("explore_database", {"table_name": "Entries", "limit": 3}, result)
        
        if result.get("success"):
            print(f"\n📊 Database Schema:")
            for col_info in result.get("schema", []):
                col_id, col_name, col_type, not_null, default_val, pk = col_info
                print(f"  - {col_name}: {col_type} {'(PRIMARY KEY)' if pk else ''}")
            
            print(f"\n📋 Sample Data (first 3 rows):")
            for i, row in enumerate(result.get("sample_data", [])[:3]):
                print(f"  Row {i+1}: {row}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_performance():
    """Demonstrate performance characteristics."""
    print_header("Performance Demo")
    
    try:
        from logeion import get_word
        import time
        
        # Test multiple word lookups
        test_words = ["amare", "puer", "bonus", "magna", "puella"]
        
        print(f"Testing performance with {len(test_words)} words...")
        
        total_time = 0
        successful_lookups = 0
        
        for word in test_words:
            start_time = time.time()
            result = get_word(word)
            end_time = time.time()
            
            lookup_time = end_time - start_time
            total_time += lookup_time
            
            if result.success:
                successful_lookups += 1
                print(f"  ✅ '{word}': {lookup_time:.4f}s")
            else:
                print(f"  ❌ '{word}': {lookup_time:.4f}s (not found)")
        
        avg_time = total_time / len(test_words)
        success_rate = (successful_lookups / len(test_words)) * 100
        
        print(f"\n📊 Performance Summary:")
        print(f"  - Total time: {total_time:.4f}s")
        print(f"  - Average lookup time: {avg_time:.4f}s")
        print(f"  - Success rate: {success_rate:.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print_header("Error Handling Demo")
    
    try:
        from logeion import get_word
        
        # Test with invalid input
        print("Testing error handling with invalid database path...")
        
        # Temporarily modify the database path to test error handling
        import logeion
        original_path = logeion.DATABASE_PATH
        logeion.DATABASE_PATH = "/invalid/path/database.sqlite"
        
        result = get_word("test")
        print_result("get_word (invalid DB)", {"word": "test"}, result)
        
        # Restore original path
        logeion.DATABASE_PATH = original_path
        
        print(f"\n✅ Error handling test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all demos."""
    print("🚀 Logeion MCP Server Demo")
    print("This demo showcases the capabilities of the Latin dictionary MCP server.")
    
    try:
        # Check if the server can be imported
        import logeion
        print(f"✅ Server module loaded successfully")
        print(f"📍 Database path: {logeion.DATABASE_PATH}")
        
        # Run demos
        demo_server_info()
        demo_word_search()
        demo_database_exploration()
        demo_performance()
        demo_error_handling()
        
        print_header("Demo Complete")
        print("🎉 All demos completed successfully!")
        print("\nTo run the MCP server:")
        print("  python logeion.py")
        print("\nTo run tests:")
        print("  python test_logeion.py")
        print("\nTo build Docker image:")
        print("  docker build -t logeion-mcp-server .")
        
    except ImportError as e:
        print(f"❌ Failed to import server module: {e}")
        print("Make sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")
        print("  python -m spacy download la_core_web_lg")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Check that the database file exists and is accessible.")

if __name__ == "__main__":
    main()
