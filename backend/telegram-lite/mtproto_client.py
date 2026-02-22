"""
MTProto Client Module for Telegram Intelligence
Uses Pyrogram with pre-authorized StringSession
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from pyrogram import Client
from pyrogram.errors import (
    FloodWait,
    ChannelPrivate,
    UsernameNotOccupied,
    UsernameInvalid,
    ChatAdminRequired,
)

logger = logging.getLogger(__name__)

# Pre-authorized session string (Pyrogram format)
SESSION_STRING = "AgI63nUAX2BylpxKN4ud5nHMnr2PEnzfX7SxpquHjaQfyRdpcid3hCAA8hbwsfvnfvxWHz0ljpejYeIHKKbY626FG99TDVkakkVdU_-n3-QZ9Xi2lfZ-sEEB3R4H4C5eV2DcjzToZUUxUM624yNc98Z-yJj7fls6ZMXKE4JL2R6nYwoaS0sCB_bXolx5lMoAmRDrL74fz7jW1t8W5k2_XQRyD1bwG2Y07oRV_d4hkKDJiGyoGmtxpjeMnswcFpb5e66tY4yCTgUyWTr1gQqckOuIzIQWShm3v45IGPalwxyBHjTj1sgD5lxNjSunVSY7jv-jIaN1hgPhTbSEeiqQn4Cqh9dd3QAAAAHnyPCPAA"

# API credentials
API_ID = 37412469
API_HASH = "b4ffe2277c3041f29deec2627f877f5a"


class MTProtoClient:
    """
    Singleton MTProto client using Pyrogram.
    """
    _instance = None
    _client: Optional[Client] = None
    _connected: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'MTProtoClient':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def connect(self) -> bool:
        """Connect using pre-authorized StringSession."""
        if self._connected and self._client:
            return True
        
        try:
            self._client = Client(
                name="telegram_intel",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=SESSION_STRING,
                in_memory=True
            )
            
            await self._client.start()
            self._connected = True
            
            me = await self._client.get_me()
            logger.info(f"Connected as: {me.username or me.phone_number or me.id}")
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Disconnect the client"""
        if self._client and self._connected:
            await self._client.stop()
            self._connected = False
            logger.info("Disconnected from Telegram")
    
    async def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._connected and self._client is not None
    
    async def get_channel_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetch channel/group information."""
        if not await self.connect():
            return None
        
        clean_username = username.lower().replace('@', '').strip()
        
        try:
            chat = await self._client.get_chat(clean_username)
            
            return {
                'username': clean_username,
                'title': chat.title or clean_username,
                'about': chat.description or '',
                'participantsCount': chat.members_count or 0,
                'isChannel': chat.type.value == 'channel',
                'isMegagroup': chat.type.value == 'supergroup',
                'linkedChatId': chat.linked_chat.id if chat.linked_chat else None,
            }
            
        except ChannelPrivate:
            logger.warning(f"Channel {clean_username} is private")
            return {'error': 'PRIVATE', 'username': clean_username}
            
        except UsernameNotOccupied:
            logger.warning(f"Username {clean_username} not found")
            return {'error': 'NOT_FOUND', 'username': clean_username}
            
        except UsernameInvalid:
            logger.warning(f"Invalid username: {clean_username}")
            return {'error': 'INVALID', 'username': clean_username}
            
        except FloodWait as e:
            logger.error(f"Flood wait: {e.value}s")
            return {'error': 'FLOOD_WAIT', 'seconds': e.value}
            
        except Exception as e:
            logger.error(f"Error fetching channel {clean_username}: {e}")
            return {'error': 'UNKNOWN', 'message': str(e)}
    
    async def get_channel_messages(
        self, 
        username: str, 
        limit: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """Fetch recent messages from a channel."""
        if not await self.connect():
            return None
        
        clean_username = username.lower().replace('@', '').strip()
        
        try:
            messages = []
            async for msg in self._client.get_chat_history(clean_username, limit=min(limit, 1000)):
                messages.append({
                    'messageId': msg.id,
                    'date': msg.date.isoformat() if msg.date else None,
                    'text': msg.text or msg.caption or '',
                    'views': msg.views or 0,
                    'forwards': msg.forwards or 0,
                    'hasMedia': msg.media is not None,
                    'mediaType': str(msg.media) if msg.media else None,
                })
            
            return messages
            
        except FloodWait as e:
            logger.error(f"Flood wait on messages: {e.value}s")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching messages from {clean_username}: {e}")
            return None
    
    async def resolve_mentions(self, text: str) -> List[str]:
        """Extract @mentions from text."""
        import re
        mentions = re.findall(r'@([a-zA-Z][a-zA-Z0-9_]{3,30})', text)
        return list(set(m.lower() for m in mentions if len(m) >= 5))


def get_mtproto_client() -> MTProtoClient:
    """Get the singleton MTProto client instance"""
    return MTProtoClient.get_instance()


class MTProtoConnection:
    """Context manager for MTProto connections"""
    
    def __init__(self):
        self.client = get_mtproto_client()
    
    async def __aenter__(self) -> MTProtoClient:
        await self.client.connect()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass  # Keep connection alive
