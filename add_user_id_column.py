"""
Add user_id column to resumes table
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text, create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def add_user_id_column():
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='resumes' AND column_name='user_id'
        """))
        
        if result.fetchone():
            print("✓ user_id column already exists")
            return
        
        print("Adding user_id column to resumes table...")
        
        # Add the column
        conn.execute(text("""
            ALTER TABLE resumes 
            ADD COLUMN user_id INTEGER REFERENCES users(id)
        """))
        conn.commit()
        
        print("✓ Successfully added user_id column!")

if __name__ == "__main__":
    try:
        add_user_id_column()
        print("\n✅ Database migration complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
