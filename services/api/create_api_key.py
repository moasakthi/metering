#!/usr/bin/env python3
"""Script to create an API key for development."""

import hashlib
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import MeteringAPIKey
from app.config import settings

def create_api_key(api_key: str, name: str = "Development Key"):
    """Create an API key in the database."""
    # Hash the key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Connect to database
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check if key already exists
    existing = session.query(MeteringAPIKey).filter(
        MeteringAPIKey.key_hash == key_hash
    ).first()
    
    if existing:
        print(f"API Key already exists: {api_key}")
        print(f"Name: {existing.name}")
        print(f"Active: {existing.is_active}")
        return
    
    # Create API key
    api_key_obj = MeteringAPIKey(
        key_hash=key_hash,
        name=name,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    session.add(api_key_obj)
    session.commit()
    
    print("=" * 60)
    print("API Key Created Successfully!")
    print("=" * 60)
    print(f"API Key: {api_key}")
    print(f"Name: {name}")
    print(f"\nUse this in your requests:")
    print(f"  Header: X-API-Key: {api_key}")
    print(f"\nOr set in .env file:")
    print(f"  VITE_API_KEY={api_key}")
    print("=" * 60)
    
    session.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        name = sys.argv[2] if len(sys.argv) > 2 else "Development Key"
    else:
        # Default development key
        api_key = "dev_key_12345"
        name = "Development Key"
        print("Using default API key. You can specify custom key:")
        print("  python3 create_api_key.py <your_key> [name]")
        print()
    
    create_api_key(api_key, name)

