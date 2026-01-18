"""
Simple database connection diagnostic script
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env file")
    sys.exit(1)

# Mask password
parts = DATABASE_URL.split("@")
if len(parts) == 2:
    masked = f"postgresql://***@{parts[1]}"
else:
    masked = "***"

print(f"DATABASE_URL format: {masked}")
print(f"\nAttempting connection...")

# Fix: Force usage of psycopg (v3) driver if psycopg2 is missing
# We installed psycopg[binary] (v3) because v2 fails on Python 3.14
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
    print("ℹ️  Updated driver to 'postgresql+psycopg' (Psycopg 3)")

try:
    from sqlalchemy import create_engine, text
    
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"\n✅ SUCCESS! Connected to PostgreSQL")
        print(f"Version: {version}")
        
except Exception as e:
    print(f"\n❌ CONNECTION FAILED")
    print(f"Error: {e}")
    print(f"\nTroubleshooting:")
    print("1. Check if your Neon database is active (not paused)")
    print("2. Verify the DATABASE_URL format")
    print("3. Check your internet connection")
    sys.exit(1)
