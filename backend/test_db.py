"""Test database connection to Neon."""
import asyncio
from app.database import engine, async_session_maker, Base
from app.models import User, Department, Section, Faculty, Course, Room
from sqlalchemy import text


async def test_connection():
    """Test database connection and create tables."""
    print("Testing Neon database connection...")
    
    try:
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Connected to PostgreSQL: {version}")
            
            # Create all tables
            print("\nCreating tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✓ Tables created successfully")
            
            # List tables
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            print(f"\n✓ Created {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
        
        print("\n✓ Database setup complete!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())
