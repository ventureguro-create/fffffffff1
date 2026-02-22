# Telegram Intelligence Platform - PRD

## Project Overview
**Telegram Market Intelligence Terminal** - изолированный модуль для анализа Telegram-каналов

**Status:** UI Integration + MTProto Module Complete ✅
**Last Updated:** 2026-02-22
**Version:** 1.2.0

---

## What's Implemented

### Frontend (React) - P0 Complete ✅

#### UI Components
- ✅ **Sparkline Charts** - mini trend charts в таблице каналов
- ✅ **ChannelChart** - полноценный recharts график на странице деталей
- ✅ **FilterDrawer** - URL-driven фильтры с presets
- ✅ **Quick Presets** - Fast Growing, High Reach Low Spam, Low Risk Stable, New Emerging
- ✅ **Filter Fields** - Type, Activity Level, Members range, Reach range, Growth range, Red Flags, Sort
- ✅ **Compare Modal** - сравнение двух каналов (исправлен баг с null safety)

#### Pages
- ✅ `/telegram` - Entities Overview с sparkline trends
- ✅ `/telegram/:username` - Channel Overview с Performance Timeline chart
- ✅ AppLayout с Sidebar и TopBar (оригинальный дизайн FOMO)

#### Libraries
- ✅ `recharts` - для Sparkline и ChannelChart компонентов

### Backend (FastAPI Python) - Complete ✅

#### Core Modules (`/app/backend/telegram-lite/`)
- ✅ `policy.py` - Конфигурация ingestion (rps, flood thresholds, min subscribers, lang gate)
- ✅ `safe_mode.py` - SAFE MODE система: flood counters, автоматическая активация
- ✅ `scheduler.py` - SafeScheduler: очередь каналов по stage/priority
- ✅ `lang_crypto.py` - RU/UA Language Gate + Crypto Relevance Scoring
- ✅ `members_proxy.py` - Proxy Members estimation
- ✅ `priority.py` - Top-Down scheduling
- ✅ `discovery.py` - Discovery Expansion: mentions + forwards → candidates
- ✅ `seeds.py` - Seeds Import helper
- ✅ `query_builder.py` - Filter API query builder
- ✅ **`mtproto_client.py`** - Telethon MTProto клиент (P1)

#### API Endpoints
- ✅ `GET /api/telegram-intel/utility/list` - с sparkline данными
- ✅ `GET /api/telegram-intel/channel/:username/overview` - с timeline для charts
- ✅ `POST /api/telegram-intel/admin/seeds/import` - импорт seed usernames
- ✅ `GET /api/telegram-intel/admin/census/summary` - распределение по stage
- ✅ `GET /api/telegram-intel/admin/census/status` - очередь, safe mode
- ✅ `GET /api/telegram-intel/admin/mtproto/status` - статус MTProto клиента
- ✅ `POST /api/telegram-intel/admin/mtproto/connect` - подключение клиента
- ✅ `GET /api/telegram-intel/admin/mtproto/fetch/:username` - live fetch канала
- ✅ `GET /api/telegram-intel/admin/mtproto/messages/:username` - fetch сообщений

### MTProto Integration (P1) - Partial ✅

#### Installed
- ✅ Telethon 1.42.0
- ✅ cryptg (performance optimization)
- ✅ MTProto client module с session management
- ✅ Flood wait handling with exponential backoff
- ✅ Channel info + messages fetching

#### Pending
- ⏳ **TG_API_ID required** - credentials содержат только TG_API_KEY (api_hash), нужен api_id
- ⏳ Manual authorization (`python auth_telegram.py`)

### Data Storage (MongoDB)
- ✅ `tg_channel_states` - состояние каналов + stage/priority/nextAllowedAt
- ✅ `tg_channels` - UI data с метриками
- ✅ `tg_posts` - посты каналов
- ✅ `tg_score_snapshots` - snapshots метрик
- ✅ `tg_discovery_edges` - provenance (как найден канал)
- ✅ `tg_watchlist` - пользовательский watchlist

---

## Testing Results (2026-02-22)

### Backend: 100% ✅
- 31 тестов пройдено
- Все API endpoints работают
- Sparkline данные генерируются корректно

### Frontend: 95% ✅
- Таблица с трендами работает
- Фильтры и presets работают
- Channel detail page с графиком работает
- Compare modal исправлен

---

## Secrets Management

### Encrypted Credentials
- **File:** `/app/backend/.secrets/tg_credentials.enc`
- **Key:** `/app/backend/.secrets/DECRYPTION_KEY.txt`
- **Contents:** TG_PHONE, TG_API_KEY (api_hash)
- **Missing:** TG_API_ID (нужно для MTProto авторизации)

---

## Backlog / Next Steps

### P0 (Blocker) - User Action Required
- [ ] **Предоставить TG_API_ID** для MTProto авторизации
- [ ] Запустить `python auth_telegram.py` для авторизации

### P1 (High)
- [ ] Cron jobs для автоматического обновления (12-24h)
- [ ] Watchlist кнопка на Channel Page

### P2 (Medium)
- [ ] AI Summary с OpenAI GPT
- [ ] Dark mode theme
- [ ] Export to CSV

### P3 (Low)
- [ ] Compare multiple channels
- [ ] Trend alerts / notifications

---

## Files Reference

### Frontend
- `/app/frontend/src/pages/TelegramEntitiesPage.jsx` - main list page
- `/app/frontend/src/pages/TelegramChannelOverviewPage.jsx` - channel detail page
- `/app/frontend/src/modules/telegram/components/Sparkline.jsx` - trend chart
- `/app/frontend/src/modules/telegram/components/ChannelChart.jsx` - full chart
- `/app/frontend/src/components/telegram/TelegramFilterDrawer.jsx` - filter UI

### Backend
- `/app/backend/server.py` - main API server
- `/app/backend/telegram-lite/mtproto_client.py` - MTProto client
- `/app/backend/auth_telegram.py` - one-time auth script

---

## Architecture

```
/app
├── backend/
│   ├── server.py                 # FastAPI server (1400+ lines)
│   ├── auth_telegram.py          # Manual auth script
│   ├── .secrets/                 # Encrypted credentials
│   ├── .sessions/                # Telethon session files
│   └── telegram-lite/            # Core modules
│       ├── mtproto_client.py     # Telethon wrapper
│       ├── policy.py
│       ├── scheduler.py
│       └── ... (other modules)
└── frontend/
    └── src/
        ├── pages/
        │   ├── TelegramEntitiesPage.jsx
        │   └── TelegramChannelOverviewPage.jsx
        ├── modules/telegram/components/
        │   ├── Sparkline.jsx
        │   └── ChannelChart.jsx
        └── components/telegram/
            └── TelegramFilterDrawer.jsx
```
