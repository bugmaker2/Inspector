#!/usr/bin/env python3
"""
Test script for bilingual summary generation functionality.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the app directory to the Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
app_dir = project_root / "app"
sys.path.insert(0, str(app_dir))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database.database import SessionLocal
from app.models.member import Member, Activity, Summary
from app.services.summarizers.llm_summarizer import LLMSummarizer
from app.core.config.settings import settings

async def test_bilingual_summary_generation():
    """Test bilingual summary generation."""
    print("🧪 Testing Bilingual Summary Generation")
    print("=======================================")
    
    # Check if OpenAI is configured
    if not settings.openai_api_key:
        print("❌ OpenAI API key not configured")
        print("Please set OPENAI_API_KEY in your environment")
        return False
    
    db = SessionLocal()
    try:
        # Create test member
        test_member = Member(
            name="Test User",
            email="test@example.com",
            position="Software Engineer",
            department="Engineering"
        )
        db.add(test_member)
        db.commit()
        db.refresh(test_member)
        
        # Create test activities
        test_activities = [
            Activity(
                member_id=test_member.id,
                social_profile_id=1,  # We'll use a dummy ID
                platform="github",
                activity_type="commit",
                title="Add new feature",
                content="Implemented user authentication system",
                url="https://github.com/test/repo/commit/123",
                published_at=datetime.utcnow() - timedelta(hours=2)
            ),
            Activity(
                member_id=test_member.id,
                social_profile_id=1,
                platform="linkedin",
                activity_type="post",
                title="Professional milestone",
                content="Excited to share that I've completed a major project milestone",
                url="https://linkedin.com/posts/test",
                published_at=datetime.utcnow() - timedelta(hours=1)
            )
        ]
        
        for activity in test_activities:
            db.add(activity)
        db.commit()
        
        print(f"✅ Created test member: {test_member.name}")
        print(f"✅ Created {len(test_activities)} test activities")
        
        # Test LLM summarizer
        summarizer = LLMSummarizer(db)
        
        if not summarizer.can_summarize():
            print("❌ LLM summarizer is not available")
            return False
        
        print("✅ LLM summarizer is available")
        
        # Test bilingual content generation
        print("🔄 Testing bilingual content generation...")
        
        # Get activities for today
        today = datetime.utcnow().date()
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        
        activities = db.query(Activity).filter(
            Activity.created_at >= start_date,
            Activity.created_at <= end_date
        ).all()
        
        if not activities:
            print("❌ No activities found for today")
            return False
        
        print(f"✅ Found {len(activities)} activities for testing")
        
        # Test the bilingual content generation method
        try:
            bilingual_content = await summarizer._generate_summary_content(
                activities, "daily", start_date, end_date
            )
            
            if bilingual_content and "chinese" in bilingual_content and "english" in bilingual_content:
                print("✅ Bilingual content generation successful")
                print(f"   Chinese content length: {len(bilingual_content['chinese'])} characters")
                print(f"   English content length: {len(bilingual_content['english'])} characters")
                
                # Show preview of content
                print("\n📝 Chinese Content Preview:")
                print(bilingual_content['chinese'][:200] + "...")
                print("\n📝 English Content Preview:")
                print(bilingual_content['english'][:200] + "...")
                
                return True
            else:
                print("❌ Bilingual content generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Error during bilingual content generation: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        db.close()

def test_database_schema():
    """Test if the database schema supports bilingual content."""
    print("\n🗄️  Testing Database Schema")
    print("============================")
    
    try:
        # Use direct SQLite connection instead of SQLAlchemy for schema check
        import sqlite3
        conn = sqlite3.connect("inspector.db")
        cursor = conn.cursor()
        
        # Check if content_en column exists
        cursor.execute("PRAGMA table_info(summaries)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'content_en' in columns:
            print("✅ content_en column exists in summaries table")
            return True
        else:
            print("❌ content_en column not found in summaries table")
            print("Please run the migration script: python scripts/migrate_bilingual_summary.py")
            return False
            
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Main test function."""
    print("🚀 Inspector Bilingual Summary Test")
    print("====================================")
    
    # Test database schema first
    schema_ok = test_database_schema()
    if not schema_ok:
        print("\n❌ Database schema test failed. Please run migration first.")
        sys.exit(1)
    
    # Test bilingual summary generation
    generation_ok = asyncio.run(test_bilingual_summary_generation())
    
    if generation_ok:
        print("\n✅ All tests passed!")
        print("Bilingual summary generation is working correctly.")
    else:
        print("\n❌ Some tests failed.")
        print("Please check your configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 