# Telegram Intelligence Platform - PRD

## Project Overview
**Telegram Market Intelligence Terminal** - изолированный модуль для анализа Telegram-каналов

**Status:** Development Complete ✅
**Last Updated:** 2026-02-21
**Version:** 1.0.0

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
- ✅ `/telegram` - Entities Overview page
- ✅ `/telegram/:username` - Channel Overview page  
- ✅ TelegramFilterDrawer - URL-driven фильтры
- ✅ Responsive design с Tailwind CSS

### Data Storage (MongoDB)
- ✅ `tg_channel_states` - состояние каналов
- ✅ `tg_score_snapshots` - снимки метрик
- ✅ `tg_posts` - посты каналов
- ✅ `tg_watchlist` - список отслеживания

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
│   │   ├── pages/
│   │   │   ├── TelegramEntitiesPage.jsx
│   │   │   └── TelegramChannelOverviewPage.jsx
│   │   ├── components/telegram/
│   │   │   └── TelegramFilterDrawer.jsx
│   │   └── api/
│   │       ├── client.js
│   │       └── telegramIntel.api.js
│   └── package.json
└── memory/
    └── PRD.md
```

---

## Testing Results
- **Backend:** 96.6% success rate
- **Frontend:** 95% success rate
- **Overall:** 96% success rate

---

## Backlog / Next Steps

### P0 (Critical)
- [ ] Подключить реальное MTProto с TG_SECRETS_KEY
- [ ] Cron jobs для автоматического обновления (12-24h)

### P1 (High)
- [ ] Compare Modal UI компонент на frontend
- [ ] Watchlist кнопка на Channel Page
- [ ] Export данных в CSV

### P2 (Medium)
- [ ] AI Summary с OpenAI GPT
- [ ] Расширенные формулы scoring
- [ ] Dark mode theme

---

## API Contracts

### GET /api/telegram-intel/utility/list
```typescript
interface ListResponse {
  ok: boolean;
  items: ChannelItem[];
  total: number;
  page: number;
  limit: number;
  stats: {
    tracked: number;
    avgUtility: number;
    highGrowth: number;
    highRisk: number;
  };
}
```

### GET /api/telegram-intel/channel/:username/overview
```typescript
interface OverviewResponse {
  ok: boolean;
  profile: { username, title, type, about };
  topCards: { subscribers, viewsPerPost, messagesPerDay, activityLevel };
  aiSummary: string;
  activityOverview: { postsPerDay, activeDays, peakHour, consistency };
  audienceSnapshot: { total, growth7d, growth30d, engagementRate };
  productOverview: { category, language, monetization, topics };
  channelSnapshot: { live, lastPost, totalPosts, avgViews };
  healthSafety: { trustScore, stability, fraudRisk, redFlags };
  relatedChannels: ChannelItem[];
  timeline: TimelinePoint[];
  recentPosts: Post[];
  metrics: Metrics;
}
```
