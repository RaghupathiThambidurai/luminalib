#!/usr/bin/env python3
"""
Insert a test user into the PostgreSQL database for borrow/return testing.
"""
import sys
import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://luminallib_user:luminallib_pass@localhost:5432/luminallib")

# Import models
sys.path.insert(0, "/Users/nagarajan.k/Documents/FullStack/luminallib-backend")
from app.adapters.db.models import UserModel, Base

def insert_test_user():
    """Insert a test user into the database."""
    try:
        # Create engine and establish connection
        engine = create_engine(DATABASE_URL, echo=False)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        with Session(engine) as session:
            # Check if user already exists
            existing_user = session.query(UserModel).filter(
                UserModel.username == "user_anonymous"
            ).first()
            
            if existing_user:
                print(f"✅ Test user 'user_anonymous' already exists (ID: {existing_user.id})")
                return existing_user.id
            
            # Create new test user
            user_id = str(uuid.uuid4())
            user = UserModel(
                id=user_id,
                username="user_anonymous",
                email="user_anonymous@example.com",
                full_name="Anonymous User",
                password_hash="",  # No password needed for testing
                is_active=True,
                preferences={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(user)
            session.commit()
            
            print(f"✅ Test user created successfully!")
            print(f"   - ID: {user_id}")
            print(f"   - Username: user_anonymous")
            print(f"   - Email: user_anonymous@example.com")
            
            return user_id
            
    except Exception as e:
        print(f"❌ Error inserting test user: {e}")
        raise

if __name__ == "__main__":
    insert_test_user()
