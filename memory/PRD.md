# Telegram Intelligence Platform - PRD

## Project Overview
**Telegram Market Intelligence Terminal** - изолированный модуль для анализа Telegram-каналов

**Status:** Development Complete ✅
**Last Updated:** 2026-02-22
**Version:** 1.0.1

---

## What's Implemented

### Backend (FastAPI Python)
- ✅ `/api/telegram-intel/utility/list` - список каналов с фильтрами
- ✅ `/api/telegram-intel/channel/:username/overview` - детальная страница канала
- ✅ `/api/telegram-intel/channel/:username/refresh` - обновление данных (MTProto mock)
- ✅ `/api/telegram-intel/compare` - сравнение двух каналов
- ✅ `/api/telegram-intel/watchlist` - CRUD операции с watchlist
- ✅ `/api/telegram-intel/admin/pipeline/status` - статус pipeline
- ✅ `/api/telegram-intel/admin/seed` - seed каналов
- ✅ `/api/telegram-intel/admin/ingestion/run` - batch ingestion
- ✅ `/api/telegram-intel/admin/metrics/recompute` - пересчёт метрик

### Frontend (React)
- ✅ AppLayout с Sidebar и TopBar (оригинальный дизайн FOMO)
- ✅ `/telegram` - Entities Overview page
- ✅ `/telegram/:username` - Channel Overview page  
- ✅ TelegramFilterDrawer - URL-driven фильтры
- ✅ Responsive design с Tailwind CSS
- ✅ Gilroy шрифт, скругления, правильные отступы

### Data Storage (MongoDB)
- ✅ `tg_channel_states` - состояние каналов
- ✅ `tg_score_snapshots` - снимки метрик
- ✅ `tg_posts` - посты каналов
- ✅ `tg_watchlist` - список отслеживания

---

## UI Design System

### Шрифты
- Gilroy font family
- Page titles: 28px Bold
- Section titles: 18px Semibold
- Body: 14px Medium
- Small: 12px Regular

### Скругления
- Cards: rounded-xl (12px)
- Buttons: rounded-lg (8px) / rounded-full
- Avatars: rounded-full
- Badges: rounded (4px)

### Цвета
- Primary: Teal (#14b8a6)
- Background: Gray-50 (#f9fafb)
- Cards: White
- Text: Gray-900 (primary), Gray-500 (secondary)
- Positive: Emerald-600
- Negative: Red-500

---

## Secrets Management

### Encrypted Credentials Location
- **Encrypted file:** `/app/backend/.secrets/tg_credentials.enc`
- **Decryption key:** `/app/backend/.secrets/DECRYPTION_KEY.txt`

### How to Decrypt
```python
from cryptography.fernet import Fernet
key = b'YtYLlxQ1XgP-Sy1cxXnWmwhXJOMP5HYbxVXEQ_FbzvU='
f = Fernet(key)
data = open('/app/backend/.secrets/tg_credentials.enc', 'rb').read()
print(f.decrypt(data).decode())
```

### Stored Secrets
- `TG_PHONE`: 37412469
- `TG_API_KEY`: b4ffe2277c3041f29deec2627f877f5a

---

## Architecture

```
/app/
├── backend/
│   ├── server.py              # FastAPI backend
│   ├── .secrets/
│   │   ├── tg_credentials.enc # Encrypted Telegram keys
│   │   └── DECRYPTION_KEY.txt # Fernet key
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── layout/
│   │   │   ├── AppLayout.jsx
│   │   │   └── TopBar.jsx
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   └── telegram/
│   │   │       └── TelegramFilterDrawer.jsx
│   │   ├── pages/
│   │   │   ├── TelegramEntitiesPage.jsx
│   │   │   └── TelegramChannelOverviewPage.jsx
│   │   └── api/
│   └── package.json
└── memory/
    └── PRD.md
```

---

## Backlog / Next Steps

### P0 (Critical)
- [ ] Подключить реальное MTProto с TG_SECRETS_KEY
- [ ] Cron jobs для автоматического обновления (12-24h)

### P1 (High)
- [ ] Compare Modal UI компонент
- [ ] Watchlist кнопка на Channel Page
- [ ] Export данных в CSV

### P2 (Medium)
- [ ] AI Summary с OpenAI GPT
- [ ] Расширенные формулы scoring
- [ ] Dark mode theme
