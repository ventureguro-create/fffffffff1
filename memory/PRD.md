# Telegram Intelligence Platform - PRD

## Project Overview
**Telegram Market Intelligence Terminal** - изолированный модуль для анализа Telegram-каналов

**Status:** Safe Ingestion Controls v1 Complete ✅
**Last Updated:** 2026-02-22
**Version:** 1.1.0

---

## What's Implemented

### Backend - Safe Ingestion Controls (FastAPI Python)

#### Core Modules (`/app/backend/telegram-lite/`)
- ✅ `policy.py` - Конфигурация ingestion (rps, flood thresholds, min subscribers, lang gate)
- ✅ `safe_mode.py` - SAFE MODE система: flood counters, автоматическая активация при 3 FLOOD_WAIT > 300s
- ✅ `scheduler.py` - SafeScheduler: очередь каналов по stage/priority, cadence по приоритетам
- ✅ `lang_crypto.py` - RU/UA Language Gate + Crypto Relevance Scoring (keywords + $TICKER detection)
- ✅ `members_proxy.py` - Proxy Members estimation когда participantsCount недоступен
- ✅ `priority.py` - Top-Down scheduling: большие каналы первыми
- ✅ `discovery.py` - Discovery Expansion: mentions + forwards → candidates
- ✅ `seeds.py` - Seeds Import helper
- ✅ `query_builder.py` - Filter API query builder

#### Admin Endpoints
- ✅ `POST /api/telegram-intel/admin/seeds/import` - импорт seed usernames
- ✅ `GET /api/telegram-intel/admin/census/summary` - распределение по stage + rejection breakdown
- ✅ `GET /api/telegram-intel/admin/census/status` - очередь, safe mode, recent errors
- ✅ `GET /api/telegram-intel/admin/census/lang-audit` - распределение по языку
- ✅ `POST /api/telegram-intel/admin/channel/:username/kick` - force re-queue
- ✅ `GET /api/telegram-intel/admin/channel/:username/members-audit` - members estimation audit
- ✅ `POST /api/telegram-intel/admin/discovery/run` - run discovery from posts
- ✅ `GET /api/telegram-intel/admin/discovery/recent` - recent discovery edges
- ✅ `GET /api/telegram-intel/utility/list/v2` - Enhanced Filter API with full query support

### Ingestion Rules (Census)
- ✅ **Min Subscribers**: 1000 (real OR proxy via medianViews × 4)
- ✅ **Activity Freshness**: last post ≤ 180 days
- ✅ **Language Gate**: RU/UK/mixed only
- ✅ **Crypto Relevance**: score ≥ 0.08 (keywords + tickers)

### Stages
- `CANDIDATE` - новый канал для проверки
- `PENDING` - недостаточно данных, retry позже
- `QUALIFIED` - прошёл все фильтры, готов к maintenance
- `REJECTED` - отклонён (SMALL, INACTIVE, LANG, OFFTOPIC, ERROR)

### Frontend (React)
- ✅ AppLayout с Sidebar и TopBar (оригинальный дизайн FOMO)
- ✅ `/telegram` - Entities Overview page
- ✅ `/telegram/:username` - Channel Overview page  
- ✅ TelegramFilterDrawer - URL-driven фильтры

### Data Storage (MongoDB)
- ✅ `tg_channel_states` - состояние каналов + stage/priority/nextAllowedAt
- ✅ `tg_channels` - UI data с метриками
- ✅ `tg_posts` - посты каналов
- ✅ `tg_discovery_edges` - provenance (как найден канал)
- ✅ `tg_candidate_blacklist` - TTL blacklist
- ✅ `tg_flood_events` - flood monitoring
- ✅ `tg_runtime_state` - safe mode state

---

## Secrets Management

### Encrypted Credentials
- **File:** `/app/backend/.secrets/tg_credentials.enc`
- **Key:** `/app/backend/.secrets/DECRYPTION_KEY.txt`
- **DECRYPTION_KEY:** `YtYLlxQ1XgP-Sy1cxXnWmwhXJOMP5HYbxVXEQ_FbzvU=`

```python
from cryptography.fernet import Fernet
f = Fernet(b'YtYLlxQ1XgP-Sy1cxXnWmwhXJOMP5HYbxVXEQ_FbzvU=')
print(f.decrypt(open('/app/backend/.secrets/tg_credentials.enc','rb').read()).decode())
```

---

## ENV Configuration

```bash
# Ingestion Policy
TG_RPS=1
TG_FLOOD_SLEEP_THRESHOLD=120
TG_HARD_FLOOD_BACKOFF_SEC=21600
TG_SAFE_MODE_WINDOW_SEC=600
TG_SAFE_MODE_COUNT=3
TG_SAFE_MODE_MIN_WAIT_SEC=300
TG_SAFE_MODE_DURATION_SEC=7200

# Qualification Rules
TG_MIN_SUBSCRIBERS=1000
TG_MAX_INACTIVE_DAYS=180
TG_LANG_ALLOW=ru,uk,mixed
TG_CRYPTO_MIN_SCORE=0.08

# Proxy Members
TG_PROXY_MEMBERS_ENABLED=1
TG_PROXY_MIN_MEDIAN_VIEWS=350
TG_PROXY_MULTIPLIER=4.0
```

---

## Backlog / Next Steps

### P0 (Critical) - In Progress
- [ ] Maintenance Worker (cursor-based incremental ingest)
- [ ] Connect to real MTProto runtime

### P1 (High)
- [ ] Cron jobs для автоматического обновления (12-24h)
- [ ] Compare Modal UI
- [ ] Watchlist кнопка на Channel Page

### P2 (Medium)
- [ ] AI Summary с OpenAI GPT
- [ ] Dark mode theme
