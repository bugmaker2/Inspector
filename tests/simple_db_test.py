#!/usr/bin/env python3
"""
Simple database test script.
"""

import sqlite3
from pathlib import Path

def test_database():
    """Test database connection and schema."""
    print("🧪 Simple Database Test")
    print("=======================")
    
    db_path = Path("inspector.db")
    if not db_path.exists():
        print(f"❌ Database file not found: {db_path}")
        return False
    
    print(f"✅ Database file found: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if summaries table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='summaries'")
        if cursor.fetchone():
            print("✅ summaries table exists")
        else:
            print("❌ summaries table not found")
            return False
        
        # Check table structure
        cursor.execute("PRAGMA table_info(summaries)")
        columns = cursor.fetchall()
        print(f"✅ Found {len(columns)} columns in summaries table:")
        
        column_names = []
        for column in columns:
            column_name = column[1]
            column_type = column[2]
            print(f"   - {column_name}: {column_type}")
            column_names.append(column_name)
        
        # Check for content_en column
        if 'content_en' in column_names:
            print("✅ content_en column found")
            return True
        else:
            print("❌ content_en column not found")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = test_database()
    if success:
        print("\n✅ Database test passed!")
    else:
        print("\n❌ Database test failed!") 