"""Database Indexes for Telegram Intelligence"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


async def ensure_indexes():
    """Create all necessary indexes for optimal performance"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'telegram_intel')]
    
    print("[DB] Creating indexes...")
    
    try:
        # Channel States (ingestion pipeline)
        await db.tg_channel_states.create_index("username", unique=True, background=True)
        await db.tg_channel_states.create_index([
            ("stage", 1), ("nextAllowedAt", 1), ("priority", 1)
        ], background=True)
        
        # Posts
        await db.tg_posts.create_index([("channelUsername", 1), ("messageId", 1)], unique=True, background=True)
        await db.tg_posts.create_index([("channelUsername", 1), ("date", -1)], background=True)
        await db.tg_posts.create_index("date", background=True)
        
        # Channels (UI queries)
        await db.tg_channels.create_index("username", unique=True, background=True)
        await db.tg_channels.create_index("utilityScore", background=True)
        await db.tg_channels.create_index("members", background=True)
        await db.tg_channels.create_index("avgReach", background=True)
        await db.tg_channels.create_index("growth7", background=True)
        await db.tg_channels.create_index("lang", background=True)
        await db.tg_channels.create_index("lastPostAt", background=True)
        
        # Discovery Edges
        await db.tg_discovery_edges.create_index([
            ("foundUsername", 1), ("sourceUsername", 1), ("method", 1)
        ], unique=True, background=True)
        await db.tg_discovery_edges.create_index("createdAt", background=True)
        
        # Blacklist
        await db.tg_candidate_blacklist.create_index("username", unique=True, background=True)
        
        # Watchlist
        await db.tg_watchlist.create_index("username", unique=True, background=True)
        
        # Score Snapshots
        await db.tg_score_snapshots.create_index([("username", 1), ("date", -1)], background=True)
        
        print("[DB] Indexes created successfully!")
        
    except Exception as e:
        print(f"[DB] Index creation warning: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(ensure_indexes())
