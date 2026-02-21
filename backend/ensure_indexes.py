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
    
    # Channel States (ingestion pipeline)
    await db.tg_channel_states.create_index([("username", 1)], unique=True)
    await db.tg_channel_states.create_index([
        ("stage", 1), ("nextAllowedAt", 1), ("priority", 1), ("lastIngestAt", 1)
    ])
    await db.tg_channel_states.create_index([("stage", 1), ("lastCensusAt", 1)])
    
    # Resolve Cache
    await db.tg_resolve_cache.create_index([("username", 1)], unique=True)
    await db.tg_resolve_cache.create_index([("expiresAt", 1)], expireAfterSeconds=0)
    
    # Flood Events (rolling 1h)
    await db.tg_flood_events.create_index([("ts", 1)], name="ts_1", expireAfterSeconds=3600)
    
    # Posts
    await db.tg_posts.create_index([("channelUsername", 1), ("messageId", 1)], unique=True)
    await db.tg_posts.create_index([("channelUsername", 1), ("date", -1)])
    await db.tg_posts.create_index([("date", -1)])
    
    # Channels (UI queries)
    await db.tg_channels.create_index([("username", 1)], unique=True)
    await db.tg_channels.create_index([("utilityScore", -1)])
    await db.tg_channels.create_index([("fraudRisk", 1)])
    await db.tg_channels.create_index([("members", -1)])
    await db.tg_channels.create_index([("avgReach", -1)])
    await db.tg_channels.create_index([("growth7", -1)])
    await db.tg_channels.create_index([("postsPerDay30", -1)])
    await db.tg_channels.create_index([("lang", 1)])
    await db.tg_channels.create_index([("cryptoRelevanceScore", -1)])
    await db.tg_channels.create_index([("lastPostAt", -1)])
    
    # Discovery Edges
    await db.tg_discovery_edges.create_index([
        ("foundUsername", 1), ("sourceUsername", 1), ("method", 1)
    ], unique=True)
    await db.tg_discovery_edges.create_index([("createdAt", -1)])
    
    # Blacklist (TTL)
    await db.tg_candidate_blacklist.create_index([("username", 1)], unique=True)
    await db.tg_candidate_blacklist.create_index([("expiresAt", 1)], expireAfterSeconds=0)
    
    # Watchlist
    await db.tg_watchlist.create_index([("username", 1)], unique=True)
    
    # Score Snapshots
    await db.tg_score_snapshots.create_index([("username", 1), ("date", -1)])
    
    print("[DB] Indexes created successfully!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(ensure_indexes())
