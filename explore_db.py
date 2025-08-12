#!/usr/bin/env python3
import sqlite3

def explore_database():
    try:
        conn = sqlite3.connect("dvlg-wheel-mini.sqlite")
        cursor = conn.cursor()
        
        print("=== LOGEION DATABASE EXPLORATION ===")
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables found: {[t[0] for t in tables]}")
        
        # Look at Entries table structure
        cursor.execute("PRAGMA table_info(Entries);")
        columns = cursor.fetchall()
        print(f"\nEntries table columns: {[col[1] for col in columns]}")
        
        # Sample data
        cursor.execute("SELECT * FROM Entries LIMIT 3;")
        samples = cursor.fetchall()
        print("\nSample entries:")
        for i, row in enumerate(samples, 1):
            print(f"{i}. {row}")
        
        conn.close()
        print("\n✅ Database exploration complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    explore_database()