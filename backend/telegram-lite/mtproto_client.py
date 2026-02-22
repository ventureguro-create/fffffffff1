"""
MTProto Client Module for Telegram Intelligence
Handles connection to Telegram API using encrypted credentials
"""
import os
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors import (
    FloodWaitError,
    ChannelPrivateError,
    UsernameNotOccupiedError,
    UsernameInvalidError,
    ChatAdminRequiredError,
)
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# Pre-authorized session string
SESSION_STRING = "AgI63nUAX2BylpxKN4ud5nHMnr2PEnzfX7SxpquHjaQfyRdpcid3hCAA8hbwsfvnfvxWHz0ljpejYeIHKKbY626FG99TDVkakkVdU_-n3-QZ9Xi2lfZ-sEEB3R4H4C5eV2DcjzToZUUxUM624yNc98Z-yJj7fls6ZMXKE4JL2R6nYwoaS0sCB_bXolx5lMoAmRDrL74fz7jW1t8W5k2_XQRyD1bwG2Y07oRV_d4hkKDJiGyoGmtxpjeMnswcFpb5e66tY4yCTgUyWTr1gQqckOuIzIQWShm3v45IGPalwxyBHjTj1sgD5lxNjSunVSY7jv-jIaN1hgPhTbSEeiqQn4Cqh9dd3QAAAAHnyPCPAA"

class MTProtoClient:
    """
    Singleton MTProto client for Telegram API access.
    Uses pre-authorized StringSession.
    """
    _instance = None
    _client: Optional[TelegramClient] = None
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
    
    def __init__(self):
        self._credentials = None
        self._flood_wait_until = None
    
    def _load_credentials(self) -> Optional[Dict[str, Any]]:
        """Load Telegram credentials"""
        root_dir = Path(__file__).parent.parent
        key_path = root_dir / '.secrets' / 'DECRYPTION_KEY.txt'
        secrets_path = root_dir / '.secrets' / 'tg_credentials.enc'
        
        if not key_path.exists() or not secrets_path.exists():
            # Use hardcoded credentials as fallback
            return {
                'api_id': 37412469,
                'api_hash': 'b4ffe2277c3041f29deec2627f877f5a'
            }
        
        try:
            key = None
            with open(key_path, 'r') as f:
                for line in f:
                    if line.startswith('DECRYPTION_KEY='):
                        key = line.split('=', 1)[1].strip()
                        break
            
            if not key:
                return {'api_id': 37412469, 'api_hash': 'b4ffe2277c3041f29deec2627f877f5a'}
            
            fernet = Fernet(key.encode())
            with open(secrets_path, 'rb') as f:
                encrypted = f.read()
            decrypted = fernet.decrypt(encrypted)
            credentials = json.loads(decrypted.decode())
            
            # Map the keys correctly: TG_PHONE is actually api_id
            return {
                'api_id': int(credentials.get('TG_PHONE', 37412469)),
                'api_hash': credentials.get('TG_API_KEY', 'b4ffe2277c3041f29deec2627f877f5a')
            }
            
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return {'api_id': 37412469, 'api_hash': 'b4ffe2277c3041f29deec2627f877f5a'}
    
    async def connect(self) -> bool:
        """
        Initialize and connect using pre-authorized StringSession.
        """
        if self._connected and self._client:
            try:
                if await self._client.is_user_authorized():
                    return True
            except:
                pass
        
        if not self._credentials:
            self._credentials = self._load_credentials()
        
        api_id = self._credentials['api_id']
        api_hash = self._credentials['api_hash']
        
        try:
            # Use StringSession with pre-authorized session
            self._client = TelegramClient(
                StringSession(SESSION_STRING),
                api_id,
                api_hash,
                flood_sleep_threshold=60,
                request_retries=5,
                connection_retries=5,
                auto_reconnect=True,
            )
            
            await self._client.connect()
            
            if await self._client.is_user_authorized():
                self._connected = True
                me = await self._client.get_me()
                logger.info(f"Connected as: {me.username or me.phone or me.id}")
                return True
            
            logger.error("Session not authorized")
            return False
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Disconnect the client"""
        if self._client:
            await self._client.disconnect()
            self._connected = False
            logger.info("Disconnected from Telegram")
    
    async def is_connected(self) -> bool:
        """Check if client is connected and authorized"""
        if not self._client:
            return False
        try:
            return await self._client.is_user_authorized()
        except:
            return False
    
    async def get_channel_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetch channel/group information.
        Returns dict with channel metadata or None on error.
        """
        if not await self.connect():
            return None
        
        # Clean username
        clean_username = username.lower().replace('@', '').strip()
        
        try:
            # Get entity
            entity = await self._client.get_entity(clean_username)
            
            # Get full channel info
            full = await self._client(GetFullChannelRequest(channel=entity))
            
            channel = full.chats[0]
            full_chat = full.full_chat
            
            return {
                'username': clean_username,
                'title': channel.title,
                'about': full_chat.about or '',
                'participantsCount': full_chat.participants_count,
                'isChannel': not getattr(channel, 'megagroup', False),
                'isMegagroup': getattr(channel, 'megagroup', False),
                'createdAt': channel.date.isoformat() if channel.date else None,
                'linked_chat_id': full_chat.linked_chat_id,
                'can_view_participants': getattr(channel, 'participants_hidden', False) is False,
            }
            
        except ChannelPrivateError:
            logger.warning(f"Channel {clean_username} is private")
            return {'error': 'PRIVATE', 'username': clean_username}
            
        except UsernameNotOccupiedError:
            logger.warning(f"Username {clean_username} not found")
            return {'error': 'NOT_FOUND', 'username': clean_username}
            
        except UsernameInvalidError:
            logger.warning(f"Invalid username: {clean_username}")
            return {'error': 'INVALID', 'username': clean_username}
            
        except FloodWaitError as e:
            logger.error(f"Flood wait: {e.seconds}s")
            self._flood_wait_until = datetime.now(timezone.utc)
            return {'error': 'FLOOD_WAIT', 'seconds': e.seconds}
            
        except Exception as e:
            logger.error(f"Error fetching channel {clean_username}: {e}")
            return {'error': 'UNKNOWN', 'message': str(e)}
    
    async def get_channel_messages(
        self, 
        username: str, 
        limit: int = 100,
        min_id: int = 0,
        offset_date: Optional[datetime] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch recent messages from a channel.
        Returns list of message dicts or None on error.
        """
        if not await self.connect():
            return None
        
        clean_username = username.lower().replace('@', '').strip()
        
        try:
            entity = await self._client.get_entity(clean_username)
            
            messages = await self._client.get_messages(
                entity,
                limit=min(limit, 1000),  # Cap at 1000
                min_id=min_id,
                offset_date=offset_date,
            )
            
            result = []
            for msg in messages:
                result.append({
                    'messageId': msg.id,
                    'date': msg.date.isoformat() if msg.date else None,
                    'text': msg.text or '',
                    'views': msg.views or 0,
                    'forwards': msg.forwards or 0,
                    'replies': msg.replies.replies if msg.replies else 0,
                    'hasMedia': msg.media is not None,
                    'mediaType': type(msg.media).__name__ if msg.media else None,
                })
            
            return result
            
        except FloodWaitError as e:
            logger.error(f"Flood wait on messages: {e.seconds}s")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching messages from {clean_username}: {e}")
            return None
    
    async def resolve_mentions(self, text: str) -> List[str]:
        """
        Extract and resolve @mentions from text.
        Returns list of valid usernames.
        """
        import re
        
        # Find @mentions
        mentions = re.findall(r'@([a-zA-Z][a-zA-Z0-9_]{3,30})', text)
        
        valid_usernames = []
        for mention in set(mentions):
            # Quick check without full API call
            try:
                # Simple validation
                if len(mention) >= 5 and not mention.startswith('_'):
                    valid_usernames.append(mention.lower())
            except:
                pass
        
        return valid_usernames


# Global instance accessor
def get_mtproto_client() -> MTProtoClient:
    """Get the singleton MTProto client instance"""
    return MTProtoClient.get_instance()


# Async context manager for safe usage
class MTProtoConnection:
    """Context manager for MTProto connections"""
    
    def __init__(self):
        self.client = get_mtproto_client()
    
    async def __aenter__(self) -> MTProtoClient:
        await self.client.connect()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Don't disconnect - keep connection alive for reuse
        pass
