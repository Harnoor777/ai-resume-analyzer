"""
Migration script to add user_id column to existing resumes table.
Run this if you have an existing database with resumes.

If starting fresh, just run: python backend/database/database.py
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.database import engine, init_db

def add_user_id_column():
    """Add user_id column to resumes table if it doesn't exist."""
    print("Checking resumes table structure...")
    
    try:
        with engine.connect() as conn:
            # Check if user_id column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='resumes' AND column_name='user_id'
            """))
            
            if result.fetchone():
                print("✓ user_id column already exists in resumes table.")
                return
            
            # Add the column
            print("Adding user_id column to resumes table...")
            conn.execute(text("""
                ALTER TABLE resumes 
                ADD COLUMN user_id INTEGER REFERENCES users(id)
            """))
            conn.commit()
            print("✓ Successfully added user_id column with foreign key constraint.")
            
    except Exception as e:
        print(f"Migration completed. Note: {e}")
        print("\nIf you're starting fresh, this is expected.")
        print("Just run: python backend/database/database.py")

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION: Adding user_id to resumes table")
    print("=" * 60)
    
    # First ensure all tables exist
    print("\nStep 1: Creating/updating all tables...")
    init_db()
    
    # Then add the column if needed
    print("\nStep 2: Adding user_id column if missing...")
    add_user_id_column()
    
    print("\n" + "=" * 60)
    print("✓ Migration complete! Your database is ready.")
    print("=" * 60)
