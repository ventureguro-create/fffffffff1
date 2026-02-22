#!/usr/bin/env python3
"""
One-time authentication script for Telegram MTProto client.
Run this manually to authorize the client with your phone number.

Usage: python auth_telegram.py
"""
import asyncio
import json
from pathlib import Path
from cryptography.fernet import Fernet
from telethon import TelegramClient

ROOT_DIR = Path(__file__).parent

def load_credentials():
    """Load encrypted credentials"""
    key_path = ROOT_DIR / '.secrets' / 'DECRYPTION_KEY.txt'
    secrets_path = ROOT_DIR / '.secrets' / 'tg_credentials.enc'
    
    # Read key
    key = None
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
    
    return json.loads(decrypted.decode())

async def main():
    print("=== Telegram MTProto Authentication ===\n")
    
    # Load credentials
    creds = load_credentials()
    api_id = creds.get('TG_API_ID') or creds.get('api_id')
    api_hash = creds.get('TG_API_HASH') or creds.get('api_hash')
    phone = creds.get('TG_PHONE') or creds.get('phone')
    
    print(f"API ID: {api_id}")
    print(f"Phone: {phone}")
    print()
    
    # Session path
    session_dir = ROOT_DIR / '.sessions'
    session_dir.mkdir(exist_ok=True)
    session_path = session_dir / 'telegram_intel'
    
    # Create client
    client = TelegramClient(
        str(session_path),
        int(api_id),
        api_hash
    )
    
    await client.connect()
    
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Already authorized as: {me.username or me.phone}")
        print(f"User ID: {me.id}")
        await client.disconnect()
        return
    
    # Request code
    print(f"Sending code to: {phone}")
    await client.send_code_request(phone)
    
    # Get code from user
    code = input("Enter the code you received: ").strip()
    
    try:
        await client.sign_in(phone, code)
    except Exception as e:
        if 'password' in str(e).lower() or '2fa' in str(e).lower():
            password = input("2FA enabled. Enter your password: ").strip()
            await client.sign_in(password=password)
        else:
            raise
    
    me = await client.get_me()
    print(f"\nAuthenticated as: {me.username or me.phone}")
    print(f"User ID: {me.id}")
    print("\nSession saved. Client ready for use!")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
