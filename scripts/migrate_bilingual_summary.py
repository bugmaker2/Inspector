#!/usr/bin/env python3
"""
Database migration script to add bilingual support for summaries.
Adds content_en field to summaries table.
"""

import sqlite3
import os
import sys
from pathlib import Path

def migrate_database():
    """Add content_en column to summaries table."""
    
    # Get database path
    db_path = Path("inspector.db")
    if not db_path.exists():
        print("❌ Database file not found: inspector.db")
        print("Please run the application first to create the database.")
        sys.exit(1)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if content_en column already exists
        cursor.execute("PRAGMA table_info(summaries)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'content_en' in columns:
            print("✅ content_en column already exists in summaries table")
            return
        
        # Add content_en column
        print("🔄 Adding content_en column to summaries table...")
        cursor.execute("ALTER TABLE summaries ADD COLUMN content_en TEXT")
        
        # Commit changes
        conn.commit()
        print("✅ Successfully added content_en column to summaries table")
        
        # Verify the change
        cursor.execute("PRAGMA table_info(summaries)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'content_en' in columns:
            print("✅ Verification successful: content_en column is now available")
        else:
            print("❌ Verification failed: content_en column was not added")
            sys.exit(1)
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def main():
    """Main migration function."""
    print("🚀 Inspector Bilingual Summary Migration")
    print("========================================")
    
    migrate_database()
    
    print("\n✅ Migration completed successfully!")
    print("The application now supports bilingual summary generation.")
    print("You can restart the application to use the new features.")

if __name__ == "__main__":
    main() 