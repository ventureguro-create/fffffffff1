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

class MTProtoClient:
    """
    Singleton MTProto client for Telegram API access.
    Handles session management, rate limiting, and error recovery.
    """
    _instance = None
    _client: Optional[TelegramClient] = None
    _session_string: Optional[str] = None
    _connected: bool = False
    _last_flood_wait: Optional[datetime] = None
    
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
    
    def _load_encrypted_credentials(self) -> Optional[Dict[str, Any]]:
        """Load and decrypt Telegram credentials"""
        root_dir = Path(__file__).parent.parent
        key_path = root_dir / '.secrets' / 'DECRYPTION_KEY.txt'
        secrets_path = root_dir / '.secrets' / 'tg_credentials.enc'
        
        if not key_path.exists() or not secrets_path.exists():
            logger.warning("Credentials files not found")
            return None
        
        try:
            # Read decryption key
            key = None
            with open(key_path, 'r') as f:
                for line in f:
                    if line.startswith('DECRYPTION_KEY='):
                        key = line.split('=', 1)[1].strip()
                        break
            
            if not key:
                logger.error("DECRYPTION_KEY not found in file")
                return None
            
            # Decrypt credentials
            fernet = Fernet(key.encode())
            with open(secrets_path, 'rb') as f:
                encrypted = f.read()
            decrypted = fernet.decrypt(encrypted)
            
            credentials = json.loads(decrypted.decode())
            
            # Map alternative key names
            # TG_API_KEY might be the api_hash
            if 'TG_API_KEY' in credentials and 'TG_API_HASH' not in credentials:
                credentials['TG_API_HASH'] = credentials['TG_API_KEY']
            
            logger.info("Loaded encrypted Telegram credentials")
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return None
    
    async def connect(self) -> bool:
        """
        Initialize and connect the Telegram client.
        Returns True if connection successful.
        """
        if self._connected and self._client:
            return True
        
        # Load credentials
        if not self._credentials:
            self._credentials = self._load_encrypted_credentials()
        
        if not self._credentials:
            logger.error("No credentials available for connection")
            return False
        
        api_id = self._credentials.get('TG_PHONE') or self._credentials.get('TG_API_ID') or self._credentials.get('api_id')
        api_hash = self._credentials.get('TG_API_KEY') or self._credentials.get('TG_API_HASH') or self._credentials.get('api_hash')
        phone = self._credentials.get('phone')  # Phone is separate, may need to ask user
        
        if not api_id or not api_hash:
            logger.error("Missing API ID or API Hash in credentials")
            return False
        
        try:
            # Create session path
            session_dir = Path(__file__).parent.parent / '.sessions'
            session_dir.mkdir(exist_ok=True)
            session_path = session_dir / 'telegram_intel'
            
            # Create client with file-based session
            self._client = TelegramClient(
                str(session_path),
                int(api_id),
                api_hash,
                flood_sleep_threshold=60,  # Auto-sleep for waits <= 60 seconds
                request_retries=5,
                connection_retries=5,
                auto_reconnect=True,
            )
            
            await self._client.connect()
            
            # Check if already authorized
            if await self._client.is_user_authorized():
                self._connected = True
                me = await self._client.get_me()
                logger.info(f"Connected as: {me.username or me.phone}")
                return True
            
            # Need to authorize - log info for manual auth
            logger.warning(f"Client not authorized. Phone: {phone}")
            logger.info("Run manual authentication script to authorize")
            
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
