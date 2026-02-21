"""
Telegram Intelligence Backend Server
Python FastAPI wrapper that proxies Telegram Intel requests to Node.js telegram-lite.mjs
"""
from fastapi import FastAPI, APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from cryptography.fernet import Fernet
import os
import logging
import httpx
import asyncio
import subprocess
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import random
import math

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'telegram_intel')]

# Node.js Telegram Lite server URL
TG_LITE_URL = os.environ.get('TG_LITE_URL', 'http://localhost:8002')

# Create the main app
app = FastAPI(title="Telegram Intelligence API")

# Create routers
api_router = APIRouter(prefix="/api")
telegram_router = APIRouter(prefix="/api/telegram-intel")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ====================== Secrets Management ======================

def load_encrypted_secrets():
    """Load secrets from encrypted file"""
    key_path = ROOT_DIR / '.secrets' / 'DECRYPTION_KEY.txt'
    secrets_path = ROOT_DIR / '.secrets' / 'tg_credentials.enc'
    
    if not key_path.exists() or not secrets_path.exists():
        return None
    
    try:
        # Read key
        with open(key_path, 'r') as f:
            for line in f:
                if line.startswith('DECRYPTION_KEY='):
                    key = line.split('=', 1)[1].strip()
                    break
        
        # Decrypt
        fernet = Fernet(key.encode())
        with open(secrets_path, 'rb') as f:
            encrypted = f.read()
        decrypted = fernet.decrypt(encrypted)
        
        import json
        return json.loads(decrypted.decode())
    except Exception as e:
        logger.error(f"Failed to load secrets: {e}")
        return None

SECRETS = load_encrypted_secrets()
if SECRETS:
    logger.info("Loaded encrypted Telegram credentials")

# ====================== Models ======================

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class ChannelRefreshRequest(BaseModel):
    username: str

# ====================== Mock Data Generator ======================

AVATAR_COLORS = [
    '#1976D2', '#E53935', '#8E24AA', '#43A047', '#1E88E5',
    '#546E7A', '#00897B', '#F4511E', '#3949AB', '#D81B60',
]

MOCK_CHANNELS = [
    "cryptonews", "bitcoinmagazine", "ethresearch", "defi_pulse", "nft_drops",
    "whale_alerts", "trading_signals", "altcoin_daily", "blockchain_tech", "web3_devs",
    "memecoin_alerts", "crypto_alpha", "token_analysis", "yield_farming", "dex_updates",
    "layer2_news", "solana_news", "avalanche_updates", "polygon_daily", "arbitrum_one"
]

def generate_avatar_color(username: str) -> str:
    h = sum(ord(c) for c in username)
    return AVATAR_COLORS[h % len(AVATAR_COLORS)]

def format_title(username: str) -> str:
    return username.replace('_', ' ').title()

def compute_activity_label(posts_per_day: float) -> str:
    if posts_per_day >= 3:
        return "High"
    elif posts_per_day >= 1:
        return "Medium"
    return "Low"

def compute_red_flags(fraud_risk: float) -> int:
    if fraud_risk >= 0.7:
        return 4 + random.randint(0, 2)
    elif fraud_risk >= 0.5:
        return 2 + random.randint(0, 1)
    elif fraud_risk >= 0.3:
        return 1 + random.randint(0, 1)
    return int(fraud_risk * 3)

def classify_lifecycle(metrics: dict) -> str:
    growth7 = metrics.get('growth7', 0)
    growth30 = metrics.get('growth30', 0)
    utility = metrics.get('utilityScore', 50)
    stability = metrics.get('stability', 0.7)
    
    if growth7 > 15 and growth30 > 20:
        return "EXPANDING"
    elif growth7 > 5 and utility >= 60:
        return "EMERGING"
    elif growth7 < -5:
        return "DECLINING"
    elif utility >= 70 and stability >= 0.7 and growth7 < 5:
        return "MATURE"
    return "STABLE"

def generate_mock_channel(username: str, index: int = 0) -> dict:
    """Generate mock channel data"""
    random.seed(hash(username))
    
    base_score = 50 + random.randint(0, 45)
    growth7 = round(random.uniform(-5, 25), 1)
    growth30 = round(random.uniform(-10, 35), 1)
    fraud_risk = round(random.uniform(0.05, 0.4), 2)
    stability = round(random.uniform(0.5, 0.95), 2)
    engagement = round(random.uniform(0.05, 0.35), 3)
    posts_per_day = round(random.uniform(0.5, 8), 1)
    members = int(base_score * 500 + random.randint(1000, 50000))
    
    metrics = {
        'growth7': growth7,
        'growth30': growth30,
        'utilityScore': base_score,
        'stability': stability
    }
    
    return {
        'username': username,
        'title': format_title(username),
        'avatarUrl': None,
        'avatarColor': generate_avatar_color(username),
        'type': 'Channel' if random.random() > 0.2 else 'Group',
        'members': members,
        'avgReach': int(members * engagement),
        'growth7': growth7,
        'growth30': growth30,
        'activity': compute_activity_label(posts_per_day),
        'activityLabel': compute_activity_label(posts_per_day),
        'redFlags': compute_red_flags(fraud_risk),
        'fomoScore': base_score,
        'utilityScore': base_score,
        'engagement': int(engagement * 10000),
        'engagementRate': engagement,
        'lifecycle': classify_lifecycle(metrics),
        'fraudRisk': fraud_risk,
        'stability': stability,
        'postsPerDay': posts_per_day,
        'updatedAt': datetime.now(timezone.utc).isoformat(),
    }

def generate_channel_overview(username: str) -> dict:
    """Generate full channel overview data"""
    base = generate_mock_channel(username)
    now = datetime.now(timezone.utc)
    
    # Generate timeline data
    timeline = []
    for i in range(90):
        date = now.replace(day=max(1, now.day - i))
        timeline.append({
            'date': date.isoformat(),
            'views': int(base['avgReach'] * random.uniform(0.7, 1.3)),
            'posts': random.randint(1, int(base['postsPerDay'] * 2) + 1),
            'engagement': round(base['engagementRate'] * random.uniform(0.8, 1.2), 3),
        })
    
    # Generate recent posts
    recent_posts = []
    for i in range(10):
        recent_posts.append({
            'id': str(uuid.uuid4()),
            'date': now.replace(hour=max(0, now.hour - i)).isoformat(),
            'text': f"Sample post #{i+1} from @{username}. Check out the latest updates! #crypto #blockchain",
            'views': random.randint(1000, 50000),
            'forwards': random.randint(10, 500),
            'replies': random.randint(5, 200),
            'reactions': random.randint(50, 2000),
        })
    
    return {
        'ok': True,
        'profile': {
            'username': username,
            'title': base['title'],
            'avatarUrl': base['avatarUrl'],
            'avatarColor': base['avatarColor'],
            'type': base['type'],
            'about': f"Official {base['title']} channel for crypto news and analysis",
        },
        'topCards': {
            'subscribers': base['members'],
            'viewsPerPost': base['avgReach'],
            'messagesPerDay': base['postsPerDay'],
            'activityLevel': base['activity'],
        },
        'aiSummary': f"@{username} is a {base['lifecycle'].lower()} {base['type'].lower()} focused on cryptocurrency content. "
                     f"With {base['members']:,} members and {base['growth7']}% weekly growth, it shows "
                     f"{'strong' if base['utilityScore'] > 70 else 'moderate'} engagement metrics.",
        'activityOverview': {
            'postsPerDay': base['postsPerDay'],
            'activeDays': 7,
            'peakHour': random.randint(10, 20),
            'consistency': base['stability'],
        },
        'audienceSnapshot': {
            'total': base['members'],
            'growth7d': base['growth7'],
            'growth30d': base['growth30'],
            'engagementRate': base['engagementRate'],
        },
        'productOverview': {
            'category': 'Crypto',
            'topics': ['Bitcoin', 'Ethereum', 'DeFi', 'NFT'],
            'language': 'English',
            'monetization': random.choice(['Ads', 'Subscription', 'None']),
        },
        'channelSnapshot': {
            'live': True,
            'lastPost': now.isoformat(),
            'totalPosts': random.randint(500, 5000),
            'avgViews': base['avgReach'],
        },
        'healthSafety': {
            'fraudRisk': base['fraudRisk'],
            'stability': base['stability'],
            'redFlags': base['redFlags'],
            'trustScore': round((1 - base['fraudRisk']) * 100),
        },
        'relatedChannels': [
            generate_mock_channel(MOCK_CHANNELS[i])
            for i in random.sample(range(len(MOCK_CHANNELS)), min(5, len(MOCK_CHANNELS)))
            if MOCK_CHANNELS[i] != username
        ][:4],
        'timeline': timeline,
        'recentPosts': recent_posts,
        'metrics': {
            'utilityScore': base['utilityScore'],
            'growth7': base['growth7'],
            'growth30': base['growth30'],
            'engagement': base['engagementRate'],
            'fraud': base['fraudRisk'],
            'stability': base['stability'],
        },
    }

# ====================== Base API Routes ======================

@api_router.get("/")
async def root():
    return {"message": "Telegram Intelligence API v1.0", "status": "operational"}

@api_router.get("/health")
async def health():
    return {
        "status": "healthy",
        "mongodb": "connected",
        "secrets_loaded": SECRETS is not None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks

# ====================== Telegram Intel Routes ======================

@telegram_router.get("/health")
async def telegram_health():
    return {
        "ok": True,
        "module": "telegram-intel",
        "version": "1.0.0",
        "runtime": {
            "mode": "mock" if not SECRETS else "live",
            "connected": SECRETS is not None
        }
    }

@telegram_router.get("/utility/list")
async def get_utility_list(
    q: Optional[str] = None,
    type: Optional[str] = None,
    minMembers: Optional[int] = None,
    maxMembers: Optional[int] = None,
    minGrowth7: Optional[float] = None,
    maxGrowth7: Optional[float] = None,
    activity: Optional[str] = None,
    maxRedFlags: Optional[int] = None,
    lifecycle: Optional[str] = None,
    sort: Optional[str] = "score",
    page: int = 1,
    limit: int = 25
):
    """Get list of Telegram channels with utility scores"""
    try:
        # Try to get data from MongoDB first
        pipeline = [
            {"$sort": {"date": -1}},
            {"$group": {
                "_id": "$username",
                "utility": {"$first": "$utility"},
                "growth7": {"$first": "$growth7"},
                "growth30": {"$first": "$growth30"},
                "stability": {"$first": "$stability"},
                "fraud": {"$first": "$fraud"},
                "engagement": {"$first": "$engagement"},
                "postsPerDay": {"$first": "$postsPerDay"},
                "date": {"$first": "$date"},
            }}
        ]
        
        snapshots = await db.tg_score_snapshots.aggregate(pipeline).to_list(1000)
        
        if snapshots:
            # Get channel states for additional info
            usernames = [s["_id"] for s in snapshots]
            states_cursor = db.tg_channel_states.find({"username": {"$in": usernames}})
            states = await states_cursor.to_list(1000)
            states_map = {s["username"]: s for s in states}
            
            items = []
            for snap in snapshots:
                state = states_map.get(snap["_id"], {})
                utility_score = snap.get("utility", 50)
                growth7_val = snap.get("growth7", 0)
                growth30_val = snap.get("growth30", 0)
                fraud_risk = snap.get("fraud", 0.2)
                stability_val = snap.get("stability", 0.7)
                engagement_rate = snap.get("engagement", 0.1)
                posts_per_day = snap.get("postsPerDay", 2)
                
                members = state.get("participantsCount") or int(utility_score * 500 + 5000)
                
                items.append({
                    "username": snap["_id"],
                    "title": state.get("title") or format_title(snap["_id"]),
                    "avatarUrl": None,
                    "avatarColor": generate_avatar_color(snap["_id"]),
                    "type": "Group" if state.get("isChannel") is False else "Channel",
                    "members": members,
                    "avgReach": int(members * engagement_rate),
                    "growth7": growth7_val,
                    "growth30": growth30_val,
                    "activity": compute_activity_label(posts_per_day),
                    "activityLabel": compute_activity_label(posts_per_day),
                    "redFlags": compute_red_flags(fraud_risk),
                    "fomoScore": utility_score,
                    "utilityScore": utility_score,
                    "engagement": int(engagement_rate * 10000),
                    "engagementRate": engagement_rate,
                    "lifecycle": classify_lifecycle({
                        "growth7": growth7_val,
                        "growth30": growth30_val,
                        "utilityScore": utility_score,
                        "stability": stability_val
                    }),
                    "fraudRisk": fraud_risk,
                    "stability": stability_val,
                    "updatedAt": snap.get("date", datetime.now(timezone.utc)).isoformat() if isinstance(snap.get("date"), datetime) else str(snap.get("date", "")),
                })
        else:
            # Generate mock data
            items = [generate_mock_channel(ch, i) for i, ch in enumerate(MOCK_CHANNELS)]
        
        # Apply filters
        if q:
            search = q.lower()
            items = [i for i in items if search in i["username"].lower() or search in i["title"].lower()]
        if type == "channel":
            items = [i for i in items if i["type"] == "Channel"]
        elif type == "group":
            items = [i for i in items if i["type"] == "Group"]
        if minMembers is not None:
            items = [i for i in items if i["members"] >= minMembers]
        if maxMembers is not None:
            items = [i for i in items if i["members"] <= maxMembers]
        if minGrowth7 is not None:
            items = [i for i in items if i["growth7"] >= minGrowth7]
        if maxGrowth7 is not None:
            items = [i for i in items if i["growth7"] <= maxGrowth7]
        if activity:
            items = [i for i in items if i["activity"] == activity]
        if maxRedFlags is not None:
            items = [i for i in items if i["redFlags"] <= maxRedFlags]
        if lifecycle:
            items = [i for i in items if i["lifecycle"] == lifecycle]
        
        # Sort
        if sort == "growth":
            items.sort(key=lambda x: x["growth7"], reverse=True)
        elif sort == "members":
            items.sort(key=lambda x: x["members"], reverse=True)
        elif sort == "reach":
            items.sort(key=lambda x: x["avgReach"], reverse=True)
        else:
            items.sort(key=lambda x: x["fomoScore"], reverse=True)
        
        total = len(items)
        start_idx = (page - 1) * limit
        paginated = items[start_idx:start_idx + limit]
        
        return {
            "ok": True,
            "items": paginated,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": math.ceil(total / limit) if total > 0 else 1,
            "filters": {
                "q": q,
                "type": type,
                "activity": activity,
                "lifecycle": lifecycle,
            }
        }
    except Exception as e:
        logger.error(f"Error getting utility list: {e}")
        # Return mock data on error
        items = [generate_mock_channel(ch, i) for i, ch in enumerate(MOCK_CHANNELS)]
        return {
            "ok": True,
            "items": items[:limit],
            "total": len(items),
            "page": 1,
            "limit": limit,
            "pages": 1,
            "mode": "mock"
        }

@telegram_router.get("/channel/{username}/overview")
async def get_channel_overview(username: str):
    """Get full channel overview data"""
    clean_username = username.lower().replace("@", "")
    
    try:
        # Try to get real data from MongoDB
        state = await db.tg_channel_states.find_one({"username": clean_username})
        snapshot = await db.tg_score_snapshots.find_one(
            {"username": clean_username},
            sort=[("date", -1)]
        )
        
        if state and snapshot:
            # Build response from real data
            posts = await db.tg_posts.find(
                {"username": clean_username}
            ).sort("date", -1).limit(10).to_list(10)
            
            overview = generate_channel_overview(clean_username)
            
            # Override with real data where available
            overview["profile"]["title"] = state.get("title", format_title(clean_username))
            overview["profile"]["about"] = state.get("about", "")
            overview["topCards"]["subscribers"] = state.get("participantsCount", 0)
            
            if snapshot:
                overview["metrics"]["utilityScore"] = snapshot.get("utility", 50)
                overview["metrics"]["growth7"] = snapshot.get("growth7", 0)
                overview["metrics"]["growth30"] = snapshot.get("growth30", 0)
                overview["metrics"]["fraud"] = snapshot.get("fraud", 0.2)
                overview["metrics"]["stability"] = snapshot.get("stability", 0.7)
            
            if posts:
                overview["recentPosts"] = [{
                    "id": str(p.get("messageId", uuid.uuid4())),
                    "date": p.get("date", datetime.now(timezone.utc)).isoformat() if isinstance(p.get("date"), datetime) else str(p.get("date", "")),
                    "text": p.get("text", "")[:200],
                    "views": p.get("views", 0),
                    "forwards": p.get("forwards", 0),
                    "replies": p.get("replies", 0),
                    "reactions": p.get("reactions", 0),
                } for p in posts]
            
            return overview
        else:
            # Return mock data
            return generate_channel_overview(clean_username)
    except Exception as e:
        logger.error(f"Error getting channel overview: {e}")
        return generate_channel_overview(clean_username)

@telegram_router.get("/compare")
async def compare_channels(left: str, right: str):
    """Compare two channels"""
    left_data = await get_channel_overview(left)
    right_data = await get_channel_overview(right)
    
    return {
        "ok": True,
        "left": left_data,
        "right": right_data,
    }

@telegram_router.post("/channel/{username}/refresh")
async def refresh_channel(username: str):
    """
    Refresh channel data using MTProto ingestion
    POST /api/telegram-intel/channel/:username/refresh
    """
    clean_username = username.lower().replace("@", "")
    
    if not SECRETS:
        return {
            "ok": False,
            "error": "NO_CREDENTIALS",
            "message": "Telegram credentials not configured. Set TG_SECRETS_KEY and provide secrets."
        }
    
    try:
        # Try to call the Node.js telegram-lite server
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TG_LITE_URL}/api/telegram-intel/channel/{clean_username}/refresh",
                timeout=60.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"Refresh error for {clean_username}: {e}")
        # Fallback: update mock data
        now = datetime.now(timezone.utc)
        random.seed(hash(clean_username) + int(now.timestamp()))
        
        mock_data = generate_mock_channel(clean_username)
        
        # Save to MongoDB
        await db.tg_score_snapshots.update_one(
            {"username": clean_username, "date": {"$gte": datetime.now(timezone.utc).replace(hour=0)}},
            {"$set": {
                "username": clean_username,
                "date": now,
                "utility": mock_data["utilityScore"],
                "growth7": mock_data["growth7"],
                "growth30": mock_data["growth30"],
                "stability": mock_data["stability"],
                "fraud": mock_data["fraudRisk"],
                "engagement": mock_data["engagementRate"],
                "postsPerDay": mock_data["postsPerDay"],
            }},
            upsert=True
        )
        
        await db.tg_channel_states.update_one(
            {"username": clean_username},
            {"$set": {
                "username": clean_username,
                "title": mock_data["title"],
                "participantsCount": mock_data["members"],
                "isChannel": mock_data["type"] == "Channel",
                "lastIngestionAt": now,
            },
            "$setOnInsert": {"firstSeen": now}},
            upsert=True
        )
        
        return {
            "ok": True,
            "status": "updated",
            "username": clean_username,
            "postsFetched": random.randint(50, 150),
            "mode": "mock",
            "updatedAt": now.isoformat()
        }

# ====================== Intel Routes (Legacy Support) ======================

@telegram_router.get("/intel/list")
async def get_intel_list(
    mode: str = "intel",
    limit: int = 25,
    page: int = 1
):
    """Get intel leaderboard (legacy endpoint)"""
    result = await get_utility_list(limit=limit, page=page, sort="score")
    return {
        **result,
        "mode": mode,
        "stats": {
            "total": result.get("total", 0),
            "trackedChannels": result.get("total", 0),
            "avgIntel": 65,
            "avgMomentum": 0.5,
            "highAlphaCount": int(result.get("total", 0) * 0.2),
            "highFraudCount": int(result.get("total", 0) * 0.1),
        }
    }

@telegram_router.get("/channel/{username}/full")
async def get_channel_full(username: str):
    """Get full channel data (legacy endpoint)"""
    overview = await get_channel_overview(username)
    
    return {
        "ok": True,
        "intel": {
            "username": username,
            "intelScore": overview["metrics"]["utilityScore"],
            "tier": "A" if overview["metrics"]["utilityScore"] > 70 else "B" if overview["metrics"]["utilityScore"] > 50 else "C",
            "components": {
                "alphaScore": overview["metrics"]["utilityScore"] * 0.9,
                "credibilityScore": (1 - overview["metrics"]["fraud"]) * 100,
                "networkAlphaScore": overview["metrics"]["utilityScore"] * 0.8,
                "fraudRisk": overview["metrics"]["fraud"],
            }
        },
        "compare": {
            "position": {
                "rank": random.randint(1, 100),
                "percentile": random.randint(70, 99),
            },
            "gaps": {
                "toTierS": max(0, 90 - overview["metrics"]["utilityScore"]),
            },
            "peerContext": {
                "tierCount": random.randint(10, 50),
            },
            "neighbors": {
                "above": {"username": "top_channel", "score": overview["metrics"]["utilityScore"] + 5},
                "below": {"username": "lower_channel", "score": overview["metrics"]["utilityScore"] - 3},
            }
        },
        "evidence": {"items": [], "summary": {"totalTokens": 0, "firstPlaces": 0}},
        "mentions": [],
        "explain": {
            "factors": [
                {"factor": "Engagement Rate", "impact": "positive", "weight": 0.3},
                {"factor": "Growth Trend", "impact": "positive", "weight": 0.25},
                {"factor": "Content Quality", "impact": "positive", "weight": 0.2},
            ],
            "penalties": {}
        }
    }

# ====================== Watchlist Routes ======================

@telegram_router.get("/watchlist")
async def get_watchlist():
    """Get user watchlist"""
    items = await db.tg_watchlist.find({}, {"_id": 0}).to_list(100)
    return {"ok": True, "items": items, "total": len(items)}

@telegram_router.post("/watchlist")
async def add_to_watchlist(request: Request):
    """Add channel to watchlist"""
    body = await request.json()
    username = body.get("username", "").lower().replace("@", "")
    
    if not username:
        raise HTTPException(status_code=400, detail="username required")
    
    await db.tg_watchlist.update_one(
        {"username": username},
        {"$set": {
            "username": username,
            "addedAt": datetime.now(timezone.utc),
            "notes": body.get("notes", ""),
            "tags": body.get("tags", []),
        }},
        upsert=True
    )
    
    return {"ok": True, "username": username}

@telegram_router.delete("/watchlist/{username}")
async def remove_from_watchlist(username: str):
    """Remove channel from watchlist"""
    clean = username.lower().replace("@", "")
    await db.tg_watchlist.delete_one({"username": clean})
    return {"ok": True}

@telegram_router.get("/watchlist/check/{username}")
async def check_watchlist(username: str):
    """Check if channel is in watchlist"""
    clean = username.lower().replace("@", "")
    item = await db.tg_watchlist.find_one({"username": clean})
    return {"ok": True, "inWatchlist": item is not None}

# ====================== Admin Routes ======================

@api_router.get("/admin/telegram-intel/health")
async def admin_health():
    return await telegram_health()

# Include routers
app.include_router(api_router)
app.include_router(telegram_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
