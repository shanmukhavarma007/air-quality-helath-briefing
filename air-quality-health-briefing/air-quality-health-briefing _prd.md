# Air Quality & Health Risk Briefing — Production-Ready Project Document

**Version:** 1.1.0  
**Author:** Senior Engineering  
**Last Updated:** April 2026  
**Status:** Ready for Development

> **Cost Policy:** This document is written under a zero-paid-API constraint.
> Every external service used has a permanently free tier that requires no credit card
> or has been replaced with a self-hosted alternative. The only optional paid upgrade
> is the OpenRouter free model tier, which has no billing until you explicitly opt in.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Free Services Master List](#2-free-services-master-list)
3. [System Architecture](#3-system-architecture)
4. [Tech Stack](#4-tech-stack)
5. [Directory Structure](#5-directory-structure)
6. [API Integration — OpenAQ](#6-api-integration--openaq)
7. [AI Layer — OpenRouter with Hard Rate Limiting](#7-ai-layer--openrouter-with-hard-rate-limiting)
8. [Feature Specification](#8-feature-specification)
9. [UI Component Breakdown](#9-ui-component-breakdown)
10. [Database Schema](#10-database-schema)
11. [Security Implementation](#11-security-implementation)
12. [Environment Configuration](#12-environment-configuration)
13. [Backend Implementation](#13-backend-implementation)
14. [Frontend Implementation](#14-frontend-implementation)
15. [Background Jobs & Scheduling](#15-background-jobs--scheduling)
16. [Deployment](#16-deployment)
17. [Testing Strategy](#17-testing-strategy)
18. [Performance Considerations](#18-performance-considerations)
19. [Roadmap](#19-roadmap)
20. [Website Analytics](#20-website-analytics)
21. [Google SEO Protocols](#21-google-seo-protocols)

---

## 1. Project Overview

### What It Is

A full-stack, AI-powered web application that pulls real-time and historical air quality data from OpenAQ, fuses it with weather context, and generates a personalized health briefing for the user every morning. The app tells you not just *what* the air quality is — it tells you *what to do about it*, calibrated to your health profile (asthma, cardiovascular conditions, age, activity level).

### Core Value Proposition

Existing apps show a number and a colored circle. This app tells you:

- Whether it is safe to exercise outdoors today
- What time window is optimal for outdoor activity
- Whether to wear a mask and what grade
- What symptoms to expect if you have asthma or are elderly
- How today compares to your personal 30-day baseline
- A generated health brief in plain English, delivered via in-app notification or email

### Target Users

- Residents of high-pollution cities (Delhi, Visakhapatnam, Mumbai, Beijing, Jakarta)
- Parents of young children or elderly family members
- Asthmatic and cardiovascular patients
- Outdoor athletes and runners
- Corporate wellness programs

---

## 2. Free Services Master List

Every external dependency in this project is free. This table is the single reference point for cost awareness.

| Service | Purpose | Free Tier Limits | Requires Card? |
|---|---|---|---|
| OpenAQ API | Real-time air quality data | 60 req/min, generous daily limit | No |
| Open-Meteo | Weather data | Unlimited for non-commercial use | No |
| OpenRouter | AI briefing generation | Free models available; we enforce 50 req/day in code | No |
| Brevo (ex-Sendinblue) | Transactional email | 300 emails/day free forever | No |
| Supabase | PostgreSQL database | 500MB DB, 2 projects free | No |
| Upstash Redis | Redis cache + Celery broker | 10,000 commands/day free | No |
| Railway | Backend hosting | $5 free credit/month (hobby) | No — trial |
| Vercel | Frontend hosting | Unlimited hobby projects | No |
| GitHub Actions | CI/CD | 2,000 minutes/month free | No |
| Loguru + file logs | Error and application logging | Self-hosted, zero cost | No |
| PostHog Cloud | Product analytics, session recordings, funnels, feature flags | Free up to 1M events/month | No |
| Google Search Console | SEO indexing & performance | Free forever | No |

> **OpenRouter note:** OpenRouter routes to many AI providers. Free models include
> `google/gemma-3-27b-it:free`, `mistralai/mistral-7b-instruct:free`, and
> `meta-llama/llama-3.1-8b-instruct:free`. These are genuinely free with no billing.
> Our application enforces a hard cap of **50 AI requests per day** across all users
> in Redis to guarantee we never accidentally cross into a paid tier.

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                               │
│  Next.js 14 (App Router)  ·  Tailwind CSS  ·  shadcn/ui            │
│  React Query (data fetching)  ·  Recharts (visualizations)         │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTPS / REST
┌────────────────────────▼────────────────────────────────────────────┐
│                         API GATEWAY LAYER                           │
│  FastAPI (Python 3.12)  ·  Uvicorn ASGI  ·  Nginx reverse proxy    │
│  Rate Limiting (slowapi)  ·  JWT Auth  ·  Input Sanitization        │
└──────┬─────────────────┬──────────────────┬────────────────────────┘
       │                 │                  │
┌──────▼──────┐  ┌───────▼──────┐  ┌───────▼──────────────┐
│  PostgreSQL  │  │    Redis     │  │  Celery Workers       │
│  (Supabase  │  │  (Upstash —  │  │  (Scheduled briefing  │
│   free)     │  │   free tier) │  │   generation jobs)    │
└─────────────┘  └──────────────┘  └──────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────────┐
│                   EXTERNAL SERVICES (ALL FREE)                      │
│  OpenAQ API  ·  Open-Meteo (weather)  ·  OpenRouter (AI)           │
│  Brevo (email, 300/day free)                                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
User Request
  → Nginx (TLS termination, basic rate limit)
  → FastAPI (JWT validation → input sanitization → business logic)
  → Redis (cache check — return if HIT)
  → PostgreSQL (user data, stored briefings)
  → OpenAQ API (if cache MISS, fetch fresh AQI data)
  → Open-Meteo API (if cache MISS, fetch weather — no key needed)
  → Redis (check global AI quota counter — block if >= 50 today)
  → OpenRouter API (generate health brief if quota available)
  → Redis (cache result with TTL + increment daily counter)
  → Response to client
```

---

## 4. Tech Stack

### Backend

| Layer | Technology | Reason | Cost |
|---|---|---|---|
| Runtime | Python 3.12 | Mature async support, strong data ecosystem | Free |
| Framework | FastAPI 0.111 | Async-first, automatic OpenAPI docs, Pydantic validation | Free |
| ASGI Server | Uvicorn + Gunicorn | Production-grade process management | Free |
| Reverse Proxy | Nginx | TLS, rate limiting, static file serving | Free |
| Task Queue | Celery 5.x + Redis | Scheduled briefing generation, async email dispatch | Free |
| ORM | SQLAlchemy 2.x (async) | Type-safe DB access, migration support | Free |
| Migrations | Alembic | Schema versioning | Free |
| Validation | Pydantic v2 | Request/response schema enforcement, sanitization | Free |
| Auth | JWT (python-jose) + bcrypt | Stateless auth, industry-standard password hashing | Free |
| Rate Limiting | slowapi | Per-user and per-IP rate limiting on FastAPI | Free |
| Caching | Upstash Redis (free tier) | AQI data TTL caching, Celery broker, AI quota counter | Free |
| HTTP Client | httpx (async) | Non-blocking external API calls | Free |
| AI Layer | OpenRouter API (free models) | Health brief generation via free LLMs | Free |
| Email | Brevo SMTP / API (300/day) | Transactional morning briefing delivery | Free |
| Logging | Loguru | Structured application and error logging to file/stdout | Free |

### Frontend

| Layer | Technology | Reason | Cost |
|---|---|---|---|
| Framework | Next.js 14 (App Router) | SSR, RSC, built-in route handlers | Free |
| Language | TypeScript 5.x | Type safety across the full codebase | Free |
| Styling | Tailwind CSS 3.x | Utility-first, rapid UI development | Free |
| Component Library | shadcn/ui | Accessible, unstyled-base components | Free |
| Data Fetching | TanStack React Query v5 | Server state management, background refetch | Free |
| Charts | Recharts | AQI trend charts, hourly breakdowns | Free |
| Maps | Leaflet.js + react-leaflet | Station location map (OpenStreetMap tiles — free) | Free |
| Forms | React Hook Form + Zod | Client-side validation before API calls | Free |
| State | Zustand | Lightweight global state (user preferences, theme) | Free |
| Auth | next-auth v5 | Session management, JWT handling | Free |
| Icons | Lucide React | Consistent icon set | Free |
| Notifications | Sonner | Toast notification system | Free |

### Infrastructure

| Layer | Technology | Free Tier |
|---|---|---|
| Database | Supabase PostgreSQL | 500MB, 2 projects, no expiry |
| Cache / Broker | Upstash Redis | 10,000 commands/day, no expiry |
| Hosting (Backend) | Railway | $5 free credit/month |
| Hosting (Frontend) | Vercel | Unlimited hobby deploys |
| CI/CD | GitHub Actions | 2,000 free minutes/month |
| Logging | Loguru → stdout (Railway captures logs) | Free |

---

## 5. Directory Structure

```
air-quality-briefing/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entrypoint
│   │   ├── config.py                 # Settings via pydantic-settings
│   │   ├── dependencies.py           # Shared FastAPI dependencies
│   │   │
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py           # /auth/register, /auth/login, /auth/refresh
│   │   │   │   ├── users.py          # /users/me, /users/profile
│   │   │   │   ├── air_quality.py    # /aqi/current, /aqi/historical, /aqi/forecast
│   │   │   │   ├── briefings.py      # /briefings/generate, /briefings/history, /briefings/quota
│   │   │   │   └── locations.py      # /locations/search, /locations/nearby
│   │   │   └── router.py
│   │   │
│   │   ├── core/
│   │   │   ├── security.py           # JWT creation/validation, password hashing
│   │   │   ├── rate_limiter.py       # slowapi limiter + AI quota guard (Redis counter)
│   │   │   └── sanitizer.py          # Input sanitization utilities
│   │   │
│   │   ├── services/
│   │   │   ├── openaq_service.py     # OpenAQ API client
│   │   │   ├── weather_service.py    # Open-Meteo client (no API key needed)
│   │   │   ├── ai_service.py         # OpenRouter client — briefing generation
│   │   │   ├── email_service.py      # Brevo SMTP integration
│   │   │   └── cache_service.py      # Upstash Redis wrapper
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── location.py
│   │   │   ├── briefing.py
│   │   │   └── aqi_reading.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── aqi.py
│   │   │   └── briefing.py
│   │   │
│   │   ├── tasks/
│   │   │   ├── celery_app.py         # Celery instance (Upstash Redis broker)
│   │   │   ├── briefing_tasks.py     # Daily briefing generation
│   │   │   └── aqi_refresh_tasks.py  # Periodic AQI data refresh
│   │   │
│   │   └── db/
│   │       ├── session.py
│   │       └── base.py
│   │
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── dashboard/
│   │   │   ├── page.tsx
│   │   │   ├── briefing/page.tsx
│   │   │   ├── history/page.tsx
│   │   │   ├── map/page.tsx
│   │   │   └── settings/page.tsx
│   │   └── api/
│   │       └── auth/[...nextauth]/
│   │
│   ├── components/
│   │   ├── ui/                       # shadcn/ui base components
│   │   ├── aqi/
│   │   │   ├── AQIGauge.tsx
│   │   │   ├── PollutantBreakdown.tsx
│   │   │   ├── HourlyTrendChart.tsx
│   │   │   └── StationCard.tsx
│   │   ├── briefing/
│   │   │   ├── HealthBriefCard.tsx
│   │   │   ├── ActivityRecommendation.tsx
│   │   │   ├── AIQuotaBanner.tsx     # Shows remaining daily AI calls
│   │   │   └── RiskBadge.tsx
│   │   └── layout/
│   │       ├── Navbar.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   │
│   ├── lib/
│   │   ├── api.ts
│   │   ├── utils.ts
│   │   └── validators.ts
│   │
│   ├── hooks/
│   │   ├── useAQI.ts
│   │   ├── useBriefing.ts
│   │   └── useUserLocation.ts
│   │
│   ├── store/
│   │   └── userPreferences.ts
│   │
│   ├── types/index.ts
│   ├── public/
│   ├── Dockerfile
│   ├── next.config.ts
│   └── .env.local.example
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── nginx/nginx.conf
└── .github/workflows/
    ├── ci.yml
    └── deploy.yml
```

---

## 6. API Integration — OpenAQ

### Authentication

OpenAQ v3 requires a free API key passed as a header. Sign up at https://explore.openaq.org. Never hardcode. Always pull from environment.

```python
# backend/app/services/openaq_service.py

import httpx
from loguru import logger
from app.config import settings
from app.services.cache_service import CacheService

OPENAQ_BASE_URL = "https://api.openaq.org/v3"

class OpenAQService:
    def __init__(self, cache: CacheService):
        self.cache = cache
        self.headers = {
            "X-API-Key": settings.OPENAQ_API_KEY,
            "Accept": "application/json",
        }
        self.client = httpx.AsyncClient(
            base_url=OPENAQ_BASE_URL,
            headers=self.headers,
            timeout=10.0,
        )

    async def get_latest_by_location(self, lat: float, lon: float, radius: int = 10000) -> dict:
        cache_key = f"aqi:latest:{lat:.4f}:{lon:.4f}"
        cached = await self.cache.get(cache_key)
        if cached:
            logger.debug(f"Cache HIT for AQI at {lat},{lon}")
            return cached

        logger.info(f"Cache MISS — fetching OpenAQ data for {lat},{lon}")
        response = await self.client.get(
            "/locations",
            params={
                "coordinates": f"{lat},{lon}",
                "radius": radius,
                "limit": 5,
                "order_by": "distance",
            }
        )
        response.raise_for_status()
        data = response.json()
        await self.cache.set(cache_key, data, ttl=900)   # 15 minutes
        return data

    async def get_measurements(self, location_id: int, parameter: str = "pm25", limit: int = 24) -> dict:
        cache_key = f"aqi:measurements:{location_id}:{parameter}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        response = await self.client.get(
            f"/locations/{location_id}/measurements",
            params={"parameter": parameter, "limit": limit, "order_by": "datetime", "sort": "desc"}
        )
        response.raise_for_status()
        data = response.json()
        await self.cache.set(cache_key, data, ttl=600)   # 10 minutes
        return data

    async def close(self):
        await self.client.aclose()
```

### Key OpenAQ Endpoints

| Endpoint | Purpose | Cache TTL |
|---|---|---|
| `GET /v3/locations` | Find stations near coordinates | 15 min |
| `GET /v3/locations/{id}/measurements` | Get recent readings (PM2.5, PM10, O3, NO2, CO) | 10 min |
| `GET /v3/parameters` | List available pollutant parameters | 24 hours |
| `GET /v3/countries` | Country-level coverage data | 24 hours |

### Weather Data — Open-Meteo (No API Key, Completely Free)

```python
# backend/app/services/weather_service.py

import httpx
from loguru import logger
from app.services.cache_service import CacheService

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"

class WeatherService:
    def __init__(self, cache: CacheService):
        self.cache = cache
        # No auth headers needed — Open-Meteo is fully open
        self.client = httpx.AsyncClient(base_url=OPEN_METEO_BASE_URL, timeout=10.0)

    async def get_current_weather(self, lat: float, lon: float) -> dict:
        cache_key = f"weather:current:{lat:.4f}:{lon:.4f}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        response = await self.client.get(
            "/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
                "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
                "forecast_days": 1,
                "timezone": "auto",
            }
        )
        response.raise_for_status()
        data = response.json()
        await self.cache.set(cache_key, data, ttl=1800)   # 30 minutes
        return data
```

### AQI Calculation (US EPA Standard)

```python
# backend/app/services/aqi_calculator.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class AQIBreakpoint:
    c_low: float
    c_high: float
    i_low: int
    i_high: int
    category: str
    hex_color: str

PM25_BREAKPOINTS = [
    AQIBreakpoint(0.0,    12.0,   0,   50,  "Good",                   "#00E400"),
    AQIBreakpoint(12.1,   35.4,   51,  100, "Moderate",               "#FFFF00"),
    AQIBreakpoint(35.5,   55.4,   101, 150, "Unhealthy for Sensitive", "#FF7E00"),
    AQIBreakpoint(55.5,   150.4,  151, 200, "Unhealthy",              "#FF0000"),
    AQIBreakpoint(150.5,  250.4,  201, 300, "Very Unhealthy",         "#8F3F97"),
    AQIBreakpoint(250.5,  500.4,  301, 500, "Hazardous",              "#7E0023"),
]

def calculate_aqi(concentration: float, breakpoints: list[AQIBreakpoint]) -> Optional[int]:
    for bp in breakpoints:
        if bp.c_low <= concentration <= bp.c_high:
            aqi = ((bp.i_high - bp.i_low) / (bp.c_high - bp.c_low)) * (concentration - bp.c_low) + bp.i_low
            return round(aqi)
    return None
```

---

## 7. AI Layer — OpenRouter with Hard Rate Limiting

### Why OpenRouter

OpenRouter is a free AI gateway aggregating multiple providers. Free models available now:

| Model | Context | Quality |
|---|---|---|
| `google/gemma-3-27b-it:free` | 8K | High — recommended primary |
| `meta-llama/llama-3.1-8b-instruct:free` | 128K | Medium — fallback |
| `mistralai/mistral-7b-instruct:free` | 32K | Medium — fallback |

Sign up at https://openrouter.ai — no card required. Free models have no billing.

### Hard Daily Quota — 50 Requests Maximum

This is a Redis atomic counter with a 24-hour TTL that auto-resets at midnight UTC. No AI call is ever attempted without passing this gate first. This is a non-negotiable constraint — it protects against runaway costs if you later switch to a paid model by accident.

```python
# backend/app/core/rate_limiter.py

import redis.asyncio as aioredis
from datetime import datetime, timezone
from loguru import logger

DAILY_AI_QUOTA = 50

async def check_and_increment_ai_quota(redis_client: aioredis.Redis) -> tuple[bool, int]:
    """
    Atomically checks and increments the global daily AI request counter.
    Returns (allowed: bool, current_count: int).
    """
    now = datetime.now(timezone.utc)
    quota_key = f"ai_quota:{now.strftime('%Y-%m-%d')}"

    current = await redis_client.incr(quota_key)

    if current == 1:
        seconds_until_midnight = 86400 - now.hour * 3600 - now.minute * 60 - now.second
        await redis_client.expire(quota_key, seconds_until_midnight)
        logger.info(f"AI quota counter initialized for {now.date()}")

    if current > DAILY_AI_QUOTA:
        await redis_client.decr(quota_key)
        logger.warning(f"AI quota exhausted for {now.date()} — request denied")
        return False, DAILY_AI_QUOTA

    logger.info(f"AI quota: {current}/{DAILY_AI_QUOTA} used today")
    return True, current

async def get_ai_quota_remaining(redis_client: aioredis.Redis) -> int:
    now = datetime.now(timezone.utc)
    quota_key = f"ai_quota:{now.strftime('%Y-%m-%d')}"
    used = await redis_client.get(quota_key)
    used = int(used) if used else 0
    return max(0, DAILY_AI_QUOTA - used)
```

### OpenRouter AI Service

```python
# backend/app/services/ai_service.py

import httpx
import json
from loguru import logger
from app.config import settings
from app.core.rate_limiter import check_and_increment_ai_quota
from app.services.cache_service import CacheService

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

FREE_MODELS = [
    "google/gemma-3-27b-it:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
]

BRIEFING_SYSTEM_PROMPT = """You are a certified air quality health advisor.
Generate a concise, accurate, personalized health briefing based on current air
quality data and a user's health profile.

Rules:
- Write at a 7th-grade reading level. No jargon.
- Be specific. Avoid vague phrases like "take care".
- Base all health claims on WHO and EPA guidelines.
- Never diagnose. Recommend professional consultation for serious conditions.
- Output must be valid JSON only. No markdown, no extra text, no preamble."""

class QuotaExhaustedException(Exception):
    pass

class AIService:
    def __init__(self, cache: CacheService, redis_client):
        self.cache = cache
        self.redis = redis_client
        self.headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": settings.APP_URL,
            "X-Title": "Air Quality Health Briefing",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(
            base_url=OPENROUTER_BASE_URL,
            headers=self.headers,
            timeout=30.0,
        )

    async def generate_health_briefing(
        self,
        aqi_data: dict,
        weather_data: dict,
        health_profile: dict,
    ) -> dict:

        # Gate 1: Check quota FIRST
        allowed, count = await check_and_increment_ai_quota(self.redis)
        if not allowed:
            raise QuotaExhaustedException(
                "Daily AI briefing quota (50 requests) reached. Resets at midnight UTC."
            )

        # Gate 2: Check briefing cache — same AQI value + conditions combo
        cache_key = (
            f"briefing:cache:{aqi_data['aqi_value']}:"
            f"{'_'.join(sorted(health_profile.get('conditions', [])))}"
        )
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info("Returning cached briefing — decrementing quota back")
            await self.redis.decr(
                f"ai_quota:{__import__('datetime').datetime.now(__import__('datetime').timezone.utc).strftime('%Y-%m-%d')}"
            )
            return cached

        user_context = f"""
Health Profile:
- Age bracket: {health_profile['age_bracket']}
- Conditions: {', '.join(health_profile.get('conditions', [])) or 'None'}
- Activity level: {health_profile['activity_level']}

Current Air Quality:
- AQI: {aqi_data['aqi_value']} ({aqi_data['category']})
- PM2.5: {aqi_data.get('pm25', 'N/A')} µg/m³
- PM10: {aqi_data.get('pm10', 'N/A')} µg/m³
- O3: {aqi_data.get('o3', 'N/A')} µg/m³

Weather:
- Temperature: {weather_data.get('temp', 'N/A')}°C
- Humidity: {weather_data.get('humidity', 'N/A')}%
- Wind: {weather_data.get('wind_speed', 'N/A')} km/h

Hourly AQI trend: {aqi_data.get('hourly_trend', [])}

Respond ONLY with JSON in exactly this format:
{{
  "summary": "2-3 sentence overall assessment",
  "outdoor_safety": "safe|caution|avoid",
  "mask_recommendation": "string or null",
  "symptom_watch": ["symptom1", "symptom2"],
  "best_time_window": "string or null",
  "activity_guidance": "1-2 sentences",
  "historical_context": "1 sentence comparing to recent days"
}}
"""

        last_error = None
        for model in FREE_MODELS:
            try:
                logger.info(f"Attempting briefing with model: {model}")
                response = await self.client.post(
                    "/chat/completions",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": BRIEFING_SYSTEM_PROMPT},
                            {"role": "user", "content": user_context},
                        ],
                        "max_tokens": 600,
                        "temperature": 0.3,
                    }
                )
                response.raise_for_status()
                result = response.json()
                raw_text = result["choices"][0]["message"]["content"].strip()
                parsed = json.loads(raw_text)

                await self.cache.set(cache_key, parsed, ttl=7200)  # Cache 2 hours
                logger.info(f"Briefing generated with {model} (quota used: {count}/50)")
                return parsed

            except Exception as e:
                logger.warning(f"Model {model} failed: {e}. Trying next.")
                last_error = e
                continue

        raise RuntimeError(f"All free models failed. Last error: {last_error}")

    async def close(self):
        await self.client.aclose()
```

### Quota Status Endpoint

```python
# In briefings router

@router.get("/quota")
async def get_quota_status(redis=Depends(get_redis), current_user=Depends(get_current_user)):
    remaining = await get_ai_quota_remaining(redis)
    return {"daily_limit": 50, "remaining": remaining, "resets_at": "00:00 UTC"}
```

---

## 8. Feature Specification

### Core Features (MVP)

**F1 — User Registration & Onboarding**
- Email + password with email verification (via Brevo)
- Health profile: age bracket, conditions (asthma, cardiovascular, COPD, none), activity level
- Location setup with map picker
- Notification preferences: email time, alert thresholds

**F2 — Real-Time AQI Dashboard**
- Current AQI refreshed every 15 minutes
- Pollutant breakdown: PM2.5, PM10, O3, NO2, CO, SO2
- Color-coded US EPA scale gauge
- Nearest monitoring station name and distance
- Last updated timestamp with auto-refresh indicator

**F3 — AI-Generated Health Briefing (Quota-Aware)**
- Generated on-demand or once daily at user's chosen time
- Personalized to health profile
- If daily quota exhausted: returns most recent cached briefing with a timestamp notice
- Plain English, no jargon

**F4 — 30-Day Historical Trend**
- Line chart of daily AQI
- Annotations on days exceeding personal risk threshold
- Export to CSV

**F5 — Hourly Forecast View**
- 24-hour AQI projection from OpenAQ + Open-Meteo data
- Best and worst hour highlighted
- Color-coded timeline bands

**F6 — Multi-Location Management**
- Up to 3 saved locations (home, office, one more)
- Quick-switch between locations on dashboard
- Alert when any saved location enters danger zone

**F7 — Morning Email Briefing (Brevo — 300/day Free)**
- Delivered at user-configured local time (default 7am)
- Content: AQI summary, health brief, today's recommendation
- Unsubscribe link (CAN-SPAM / GDPR compliant)

**F8 — In-App Smart Alerts**
- Toast notification when AQI crosses threshold
- 2-hour cool-down between alerts for the same condition
- No push notifications in MVP (avoids paid services)

---

## 9. UI Component Breakdown

### Page: Dashboard (`/dashboard`)

```
┌─────────────────────────────────────────────────────────────┐
│  Navbar: Logo | Location Switcher | Alerts Bell | Avatar    │
├─────────────────────────────────────────────────────────────┤
│  [AIQuotaBanner — visible only when < 10 calls remain]      │
│  "10 AI briefings remaining today. Resets at midnight UTC." │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌──────────────────────────────┐  │
│  │  AQI Gauge          │  │  Today's Health Brief        │  │
│  │  ● 142              │  │  "Air quality is Unhealthy.  │  │
│  │  Unhealthy          │  │  Avoid outdoor exercise      │  │
│  │  📍 Visakhapatnam   │  │  before 5pm..."              │  │
│  │  Updated 5 min ago  │  │  [Read Full Brief →]         │  │
│  └─────────────────────┘  └──────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Pollutant Breakdown                                  │   │
│  │  PM2.5: 45µg  PM10: 78µg  O3: 32µg  NO2: 12µg      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Hourly Trend (Today)                                │   │
│  │  [Recharts AreaChart — 24h]                          │   │
│  │  Best window: 06:00–08:00 ● Worst: 14:00–17:00      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌────────────────────────┐  ┌─────────────────────────┐   │
│  │ Activity Recommendation│  │ Station Info            │   │
│  │ 🏃 Outdoor Running     │  │ 📡 VSP Station 3        │   │
│  │ ⚠️  Not Recommended   │  │ 2.3 km away             │   │
│  └────────────────────────┘  └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Interfaces

```typescript
// AQIGauge
interface AQIGaugeProps {
  value: number;
  category: string;
  hexColor: string;
  location: string;
  lastUpdated: Date;
  isLoading?: boolean;
}

// HealthBriefCard
interface HealthBriefCardProps {
  brief: {
    summary: string;
    outdoor_safety: "safe" | "caution" | "avoid";
    mask_recommendation: string | null;
    symptom_watch: string[];
    best_time_window: string | null;
    activity_guidance: string;
    generated_at: string;
    is_cached: boolean;    // True when served from cache due to quota exhaustion
  };
  isLoading?: boolean;
}

// AIQuotaBanner
interface AIQuotaBannerProps {
  remaining: number;
  dailyLimit: number;
  // Hidden when remaining >= 10
  // Amber when remaining < 10
  // Red when remaining === 0 — explains cached fallback
}

// PollutantBreakdown
interface PollutantBreakdownProps {
  readings: {
    parameter: string;
    value: number;
    unit: string;
    lastUpdated: string;
  }[];
}
```

---

## 10. Database Schema

```sql
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,        -- bcrypt cost 12
    is_verified   BOOLEAN DEFAULT FALSE,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE health_profiles (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    age_bracket    VARCHAR(20) CHECK (age_bracket IN ('child','adult','senior')),
    conditions     TEXT[] DEFAULT '{}',
    activity_level VARCHAR(20) CHECK (activity_level IN ('sedentary','moderate','athlete')),
    briefing_time  TIME DEFAULT '07:00:00',
    timezone       VARCHAR(60) DEFAULT 'UTC',
    updated_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_locations (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              UUID REFERENCES users(id) ON DELETE CASCADE,
    label                VARCHAR(100) NOT NULL,
    latitude             DECIMAL(9,6) NOT NULL,
    longitude            DECIMAL(9,6) NOT NULL,
    address              VARCHAR(255),
    openaq_location_id   INTEGER,
    is_primary           BOOLEAN DEFAULT FALSE,
    alert_threshold      INTEGER DEFAULT 150,
    sort_order           INTEGER DEFAULT 0,
    created_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE aqi_readings (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    openaq_location_id   INTEGER NOT NULL,
    parameter            VARCHAR(20) NOT NULL,
    value                DECIMAL(10,2) NOT NULL,
    unit                 VARCHAR(20) NOT NULL,
    aqi_value            INTEGER,
    recorded_at          TIMESTAMPTZ NOT NULL,
    fetched_at           TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_aqi_readings_location_time ON aqi_readings(openaq_location_id, recorded_at DESC);

CREATE TABLE briefings (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES users(id) ON DELETE CASCADE,
    location_id       UUID REFERENCES user_locations(id),
    aqi_at_generation INTEGER,
    outdoor_safety    VARCHAR(20) CHECK (outdoor_safety IN ('safe','caution','avoid')),
    brief_text        TEXT NOT NULL,
    brief_metadata    JSONB,
    model_used        VARCHAR(100),             -- OpenRouter model string
    is_cached_result  BOOLEAN DEFAULT FALSE,    -- Served from cache (quota exhausted)?
    generated_at      TIMESTAMPTZ DEFAULT NOW(),
    delivered_email   BOOLEAN DEFAULT FALSE,
    delivered_at      TIMESTAMPTZ
);
CREATE INDEX idx_briefings_user_date ON briefings(user_id, generated_at DESC);

CREATE TABLE email_verifications (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(255) UNIQUE NOT NULL,   -- SHA-256 hash
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ
);

CREATE TABLE password_resets (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(255) UNIQUE NOT NULL,   -- SHA-256 hash
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ
);

CREATE TABLE audit_log (
    id          BIGSERIAL PRIMARY KEY,
    user_id     UUID REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(100) NOT NULL,
    ip_address  INET,
    user_agent  TEXT,
    metadata    JSONB,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 11. Security Implementation

### 11.1 Password Hashing — bcrypt Cost Factor 12

```python
# backend/app/core/security.py

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": subject, "exp": expire, "iat": datetime.now(timezone.utc), "type": "access"}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": subject, "exp": expire, "iat": datetime.now(timezone.utc), "type": "refresh"}
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str, refresh: bool = False) -> dict:
    secret = settings.JWT_REFRESH_SECRET_KEY if refresh else settings.JWT_SECRET_KEY
    try:
        return jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired token")
```

### 11.2 Input Sanitization

```python
# backend/app/core/sanitizer.py

import re
import html

def sanitize_string(value: str, max_length: int = 255) -> str:
    value = html.escape(value.strip())
    value = re.sub(r'\s+', ' ', value)
    return value[:max_length]

def sanitize_coordinates(lat: float, lon: float) -> tuple[float, float]:
    lat = max(-90.0, min(90.0, lat))
    lon = max(-180.0, min(180.0, lon))
    return round(lat, 6), round(lon, 6)

def sanitize_email(email: str) -> str:
    email = email.strip().lower()
    if not re.match(r'^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$', email):
        raise ValueError("Invalid email format")
    return email[:255]
```

Pydantic v2 schema-level validation (automatic on every request body):

```python
# backend/app/schemas/auth.py

from pydantic import BaseModel, EmailStr, field_validator
import re

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("At least 8 characters required")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Must contain an uppercase letter")
        if not re.search(r'[0-9]', v):
            raise ValueError("Must contain a number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Must contain a special character")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not 2 <= len(v) <= 100:
            raise ValueError("Name must be 2–100 characters")
        if not re.match(r"^[a-zA-Z\s\-']+$", v):
            raise ValueError("Name contains invalid characters")
        return v
```

### 11.3 Rate Limiting — Two Layers

**Layer 1: Nginx (IP-level)**

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=60r/m;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=10r/m;

server {
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://backend:8000;
    }
    location /api/v1/auth/ {
        limit_req zone=auth_limit burst=5 nodelay;
        proxy_pass http://backend:8000;
    }
}
```

**Layer 2: slowapi (route-level)**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Auth routes
@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, ...): ...

@router.post("/register")
@limiter.limit("3/hour")
async def register(request: Request, ...): ...

# Briefing generation (on top of AI quota check)
@router.post("/briefings/generate")
@limiter.limit("2/30minutes")
async def generate_briefing(request: Request, ...): ...

# AQI data reads
@router.get("/aqi/current")
@limiter.limit("30/minute")
async def get_current_aqi(request: Request, ...): ...
```

### 11.4 API Key Security

Rules — no exceptions:

- `.env` is in `.gitignore` — never committed to version control
- `.env.example` contains dummy placeholder strings only
- The frontend has zero external API keys — it only ever calls your own backend
- Your backend proxies all calls to OpenAQ, Open-Meteo, OpenRouter, and Brevo
- Open-Meteo has no key at all — no secret to protect
- OpenRouter key is treated as sensitive — rotate immediately if exposed

```python
# backend/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="forbid")

    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    OPENAQ_API_KEY: str          # Free — explore.openaq.org
    OPENROUTER_API_KEY: str      # Free — openrouter.ai (free models only)
    BREVO_API_KEY: str           # Free — brevo.com (300 emails/day)
    # Open-Meteo requires no key — intentionally omitted

    APP_URL: str = "http://localhost:8000"
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    DEBUG: bool = False
    DAILY_AI_QUOTA: int = 50

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

### 11.5 CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Never "*" in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 11.6 Security Headers (Nginx)

```nginx
add_header X-Frame-Options "DENY";
add_header X-Content-Type-Options "nosniff";
add_header Referrer-Policy "strict-origin-when-cross-origin";
add_header Permissions-Policy "geolocation=(self), camera=(), microphone=()";
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 11.7 SQL Injection Prevention

```python
# CORRECT — parameterized via SQLAlchemy ORM
result = await db.execute(select(User).where(User.email == email))

# NEVER — string-formatted SQL
result = await db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### 11.8 Token Security

Raw tokens never stored in the database. Only SHA-256 hashes are persisted.

```python
import hashlib
import secrets

def generate_secure_token() -> tuple[str, str]:
    """Returns (raw_token_for_email, hashed_token_for_db)."""
    raw = secrets.token_urlsafe(32)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed
```

### 11.9 Loguru Structured Logging (Free — No External Service)

```python
# backend/app/main.py

from loguru import logger
import sys

logger.remove()

logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
    level="INFO",
    colorize=True,
)

logger.add(
    "logs/app.log",
    rotation="50 MB",
    retention="10 days",
    compression="gz",
    level="WARNING",
    # Never log secrets
    filter=lambda r: "api_key" not in r["message"].lower()
                     and "password" not in r["message"].lower(),
)
```

---

## 12. Environment Configuration

### Backend `.env.example`

```env
# ─── Database (Supabase free tier) ──────────────────────────
# Get from: supabase.com → project settings → database
DATABASE_URL=postgresql+asyncpg://postgres:password@db.YOUR_REF.supabase.co:5432/postgres

# ─── Redis (Upstash free tier) ──────────────────────────────
# Get from: console.upstash.com → create database → copy REST URL
REDIS_URL=rediss://:your_upstash_password@your_endpoint.upstash.io:6379

# ─── JWT ────────────────────────────────────────────────────
# Generate: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=REPLACE_WITH_64_CHAR_RANDOM_HEX
JWT_REFRESH_SECRET_KEY=REPLACE_WITH_DIFFERENT_64_CHAR_RANDOM_HEX
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# ─── External APIs (all free, all no credit card) ────────────
# OpenAQ: https://explore.openaq.org → sign up → get key
OPENAQ_API_KEY=your_openaq_api_key_here

# OpenRouter: https://openrouter.ai → sign up → create key → use free models only
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Brevo: https://brevo.com → sign up → SMTP & API → generate key
BREVO_API_KEY=your_brevo_api_key_here

# Open-Meteo: NO KEY NEEDED — fully open, no registration

# ─── App Config ──────────────────────────────────────────────
APP_URL=http://localhost:8000
ENVIRONMENT=development
ALLOWED_ORIGINS=["http://localhost:3000"]
DEBUG=false
DAILY_AI_QUOTA=50

# ─── Email ───────────────────────────────────────────────────
FROM_EMAIL=briefings@yourdomain.com
FROM_NAME=AirBrief
```

### Frontend `.env.local.example`

```env
# ─── Backend API ─────────────────────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# ─── Next Auth ───────────────────────────────────────────────
NEXTAUTH_SECRET=REPLACE_WITH_RANDOM_SECRET
NEXTAUTH_URL=http://localhost:3000

# NOTE: No external API keys here — ever.
# The frontend calls your own backend only.
# OpenAQ, Open-Meteo, OpenRouter, and Brevo keys
# live exclusively in the backend .env file.
```

---

## 13. Backend Implementation

### Email Service — Brevo (300 Free Emails/Day)

```python
# backend/app/services/email_service.py

import httpx
from loguru import logger
from app.config import settings

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

class EmailService:
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        }
        self.client = httpx.AsyncClient(timeout=10.0)

    async def send_briefing_email(
        self, to_email: str, to_name: str, briefing: dict, aqi_value: int, location_label: str
    ) -> bool:
        html_content = f"""
        <h2>Good morning, {to_name}</h2>
        <p><strong>Location:</strong> {location_label} | <strong>AQI:</strong> {aqi_value}</p>
        <hr>
        <p>{briefing['summary']}</p>
        <p><strong>Outdoor Safety:</strong> {briefing['outdoor_safety'].upper()}</p>
        <p><strong>Activity Guidance:</strong> {briefing['activity_guidance']}</p>
        {"<p><strong>Mask:</strong> " + briefing['mask_recommendation'] + "</p>" if briefing.get('mask_recommendation') else ""}
        {"<p><strong>Best Window:</strong> " + briefing['best_time_window'] + "</p>" if briefing.get('best_time_window') else ""}
        <hr>
        <p style="font-size:12px;color:#888;">
            <a href="{{unsubscribe}}">Unsubscribe</a>
        </p>
        """
        payload = {
            "sender": {"name": settings.FROM_NAME, "email": settings.FROM_EMAIL},
            "to": [{"email": to_email, "name": to_name}],
            "subject": f"Air Quality Brief — {location_label} | AQI {aqi_value}",
            "htmlContent": html_content,
        }
        try:
            response = await self.client.post(BREVO_API_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Briefing email sent to {to_email}")
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Brevo email failed for {to_email}: {e.response.text}")
            return False

    async def send_verification_email(self, to_email: str, to_name: str, token: str) -> bool:
        verify_url = f"{settings.APP_URL}/verify-email?token={token}"
        payload = {
            "sender": {"name": settings.FROM_NAME, "email": settings.FROM_EMAIL},
            "to": [{"email": to_email, "name": to_name}],
            "subject": "Verify your AirBrief account",
            "htmlContent": f"<p>Click to verify: <a href='{verify_url}'>{verify_url}</a></p><p>Expires in 24 hours.</p>",
        }
        try:
            response = await self.client.post(BREVO_API_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Verification email failed: {e}")
            return False

    async def close(self):
        await self.client.aclose()
```

### Cache Service — Upstash Redis

```python
# backend/app/services/cache_service.py

import json
import redis.asyncio as aioredis
from loguru import logger
from app.config import settings

class CacheService:
    def __init__(self):
        # Upstash provides rediss:// URL (TLS) — paste directly from their dashboard
        self.redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    async def get(self, key: str) -> dict | None:
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.warning(f"Redis GET failed for {key}: {e}")
            return None

    async def set(self, key: str, value: dict, ttl: int = 300) -> None:
        try:
            await self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Redis SET failed for {key}: {e}")

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
```

---

## 14. Frontend Implementation

### API Client with Auth Interceptor

```typescript
// frontend/lib/api.ts

import axios from "axios";
import { getSession, signOut } from "next-auth/react";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

api.interceptors.request.use(async (config) => {
  const session = await getSession();
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await signOut({ callbackUrl: "/login" });
    }
    if (error.response?.status === 429) {
      error.isQuotaExhausted = error.response?.data?.detail?.includes("quota");
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Zod Form Validators

```typescript
// frontend/lib/validators.ts

import { z } from "zod";

export const registerSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z
    .string()
    .min(8, "At least 8 characters")
    .regex(/[A-Z]/, "Must contain an uppercase letter")
    .regex(/[0-9]/, "Must contain a number")
    .regex(/[!@#$%^&*]/, "Must contain a special character"),
  confirmPassword: z.string(),
  fullName: z
    .string()
    .min(2, "Too short")
    .max(100, "Too long")
    .regex(/^[a-zA-Z\s\-']+$/, "Invalid characters"),
}).refine((d) => d.password === d.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
});

export const locationSchema = z.object({
  label: z.string().min(1).max(100),
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  alertThreshold: z.number().int().min(0).max(500).default(150),
});
```

---

## 15. Background Jobs & Scheduling

```python
# backend/app/tasks/celery_app.py

from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "air_quality_briefing",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.briefing_tasks", "app.tasks.aqi_refresh_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_use_ssl=True,   # Required for Upstash TLS (rediss://)
)

celery_app.conf.beat_schedule = {
    "refresh-aqi-every-15-minutes": {
        "task": "app.tasks.aqi_refresh_tasks.refresh_aqi_for_active_users",
        "schedule": crontab(minute="*/15"),
    },
    "dispatch-morning-briefings-hourly": {
        "task": "app.tasks.briefing_tasks.dispatch_morning_briefings",
        "schedule": crontab(minute="0", hour="*"),
    },
}
```

The morning briefing task checks the global AI quota before dispatching individual briefing jobs. If quota is exhausted, it serves the most recent cached briefing instead — the email still goes out, it just uses the last generated brief.

---

## 16. Deployment

### Docker Compose (Production)

```yaml
# docker-compose.prod.yml

version: "3.9"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file: ./backend/.env
    expose:
      - "8000"

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2
    restart: unless-stopped
    env_file: ./backend/.env

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.tasks.celery_app beat --loglevel=info
    restart: unless-stopped
    env_file: ./backend/.env

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/certs:/etc/nginx/certs:ro
    depends_on:
      - backend

# No db or redis containers here.
# Database = Supabase (managed, free tier)
# Redis = Upstash (managed, free tier)
# Both are external managed services — no self-hosting cost.
```

### GitHub Actions CI/CD

```yaml
# .github/workflows/deploy.yml

name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/ -v --cov=app

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g @railway/cli
          railway up --service backend

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: |
          npm install -g vercel
          cd frontend
          vercel --prod --token=$VERCEL_TOKEN
```

---

## 17. Testing Strategy

```
tests/
├── unit/
│   ├── test_aqi_calculator.py        # AQI formula at all EPA breakpoints
│   ├── test_sanitizer.py             # Input sanitization edge cases
│   ├── test_security.py              # Password hashing, JWT encode/decode
│   ├── test_ai_quota.py              # Counter increment, reset, block at 50
│   └── test_ai_service.py            # Briefing generation (mocked OpenRouter)
├── integration/
│   ├── test_auth_endpoints.py        # Register, login, refresh, logout
│   ├── test_aqi_endpoints.py         # AQI fetch with mocked OpenAQ
│   ├── test_briefing_endpoints.py    # Full briefing generation flow
│   └── test_quota_enforcement.py    # 51st request must be blocked
└── conftest.py                       # Test DB, fixtures, mock services
```

Key assertions:

- AQI calculator correct at all US EPA breakpoint boundaries
- Passwords never stored in plain text
- 6th login attempt within 1 minute returns 429
- SQL injection payloads return 422 Unprocessable Entity (Pydantic intercepts them)
- XSS payloads in name fields are escaped before storage
- AI quota counter blocks the 51st request regardless of which user makes it
- Quota counter resets at midnight UTC (TTL verified in test)
- When quota exhausted, briefing endpoint returns last cached brief with `is_cached: true`
- Email verification tokens stored in DB never match the raw token sent in email

---

## 18. Performance Considerations

- **OpenAQ cached at 15-minute TTL** — 1,000 users on the same city hit OpenAQ once per interval, not 1,000 times. Keeps you firmly inside the free tier.
- **Open-Meteo has no rate limit** — cache at 30 minutes anyway to reduce latency.
- **AI briefings cached by AQI value + health conditions** — users with the same profile and similar AQI values share a cached briefing. This is the mechanism that makes 50 daily AI calls stretch across a real user base.
- **Briefings pre-generated by Celery beat** — not on-demand at morning email delivery time.
- **Upstash 10,000 commands/day** — with 15-minute AQI caches and briefing generation, a small user base (under 50 users) fits comfortably. Monitor the Upstash dashboard. First paid tier is $0.20 per 100,000 additional commands.
- **Brevo 300 emails/day** — sufficient through beta. Scale only when needed.
- **Supabase connection limit: 20 on free tier** — set SQLAlchemy pool to 5 connections, 10 overflow.
- **React Query stale time** set to 5 minutes for AQI data.
- **Historical chart lazy loads** — 7 days default, 30 days on explicit user action.

---

## 19. Roadmap

### Phase 1 — MVP (Weeks 1–6) — Zero Cost

- [ ] User auth with email verification via Brevo
- [ ] Single location, real-time AQI from OpenAQ
- [ ] Weather context from Open-Meteo (no key needed)
- [ ] AI health briefing via OpenRouter free models (50/day hard cap enforced)
- [ ] Morning email via Brevo (300/day)
- [ ] AI quota banner in UI
- [ ] PostHog Cloud initialised; `PostHogProvider` in layout, user identity on login
- [ ] Core funnels configured: Activation, Email Retention, Briefing Engagement
- [ ] Google Search Console verified; `sitemap.xml` and `robots.txt` live

### Phase 2 — Growth (Weeks 7–12) — Still Zero Cost

- [ ] Multi-location support (up to 3)
- [ ] 30-day historical trend chart
- [ ] In-app AQI threshold alerts
- [ ] Mobile-responsive polish
- [ ] Rule-based fallback briefing when AI quota exhausted (eliminates dependency on quota)
- [ ] City landing pages for SEO (Visakhapatnam, Delhi, Mumbai, etc.) with structured data
- [ ] PostHog custom events across all key actions (briefing generated, alert set, email subscribed)

### Phase 3 — Scale (Weeks 13–20) — First Optional Spend

- [ ] Increase AI quota by switching specific routes to OpenRouter paid models (~$1–2 per 1,000 requests — still very cheap)
- [ ] Brevo paid plan when user base exceeds 300 daily active emailers
- [ ] Self-hosted push notifications via Ntfy (free, open-source)
- [ ] Weekly PDF exposure report

---

## 20. Website Analytics

### Philosophy — Product Analytics with PostHog

This project uses **PostHog** as its analytics platform. PostHog goes well beyond page view counting — it provides session recordings, funnels, cohorts, feature flags, and A/B testing, all from a single SDK. The free cloud tier (1 million events/month) is more than sufficient for MVP and early growth stages, and a self-hosted option exists if data residency ever becomes a requirement.

> **Why PostHog over Google Analytics 4?** GA4 is session-centric and optimised for marketing attribution. PostHog is product-centric — it tells you what users do inside your app (did they read the briefing? did they set an alert? where did they drop off?), which is far more actionable for a health tool with an authenticated product core.

### Analytics Service Master List

| Tool | Role | Cost |
|---|---|---|
| PostHog Cloud | Product analytics, session recording, funnels, feature flags | Free up to 1M events/month |
| Google Search Console | Organic search impressions, CTR, indexing | Free |
| Vercel Analytics (built-in) | Core Web Vitals (LCP, FID, CLS) | Free on hobby plan |

### PostHog Setup

**1. Create a free PostHog Cloud account**

Sign up at [posthog.com](https://posthog.com) — no credit card required for the free tier. Create a new project and copy your **Project API Key** (format: `phc_...`) and **Host** (`https://us.i.posthog.com` for US region or `https://eu.i.posthog.com` for EU).

Add to your frontend environment:

```env
# frontend/.env.local
NEXT_PUBLIC_POSTHOG_KEY=phc_your_project_api_key
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

**2. Install the PostHog Next.js SDK**

```bash
cd frontend
npm install posthog-js
```

**3. Create the PostHog Provider**

PostHog needs to be initialised once and made available across the React tree. Use a client component provider pattern to stay compatible with Next.js App Router's server components.

```typescript
// frontend/lib/posthog.ts

import posthog from 'posthog-js'

export function initPostHog() {
  if (typeof window === 'undefined') return

  if (!posthog.__loaded) {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
      person_profiles: 'identified_only',  // Only profile users who log in — saves event quota
      capture_pageview: false,             // We'll capture manually for App Router compatibility
      capture_pageleave: true,
      loaded: (ph) => {
        if (process.env.NODE_ENV === 'development') ph.debug()
      },
    })
  }
}

export { posthog }
```

```typescript
// frontend/components/providers/PostHogProvider.tsx
'use client'

import { useEffect } from 'react'
import { usePathname, useSearchParams } from 'next/navigation'
import { initPostHog, posthog } from '@/lib/posthog'

export function PostHogProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const searchParams = useSearchParams()

  useEffect(() => {
    initPostHog()
  }, [])

  // Manually capture page views on route change (required for App Router)
  useEffect(() => {
    if (pathname) {
      let url = window.origin + pathname
      if (searchParams?.toString()) url += `?${searchParams.toString()}`
      posthog.capture('$pageview', { '$current_url': url })
    }
  }, [pathname, searchParams])

  return <>{children}</>
}
```

```typescript
// frontend/app/layout.tsx

import { Suspense } from 'react'
import { PostHogProvider } from '@/components/providers/PostHogProvider'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Suspense>
          <PostHogProvider>
            {children}
          </PostHogProvider>
        </Suspense>
      </body>
    </html>
  )
}
```

**4. Identify Users on Login**

Connect PostHog anonymous sessions to your authenticated users so you can track behaviour across sessions and build cohorts by health profile.

```typescript
// frontend/hooks/usePostHogIdentify.ts
'use client'

import { useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { posthog } from '@/lib/posthog'

export function usePostHogIdentify() {
  const { data: session, status } = useSession()

  useEffect(() => {
    if (status === 'authenticated' && session?.user) {
      posthog.identify(session.user.id, {
        email: session.user.email,
        // Send health profile dimensions for cohort analysis
        // Do NOT send raw condition names if you want to avoid HIPAA-adjacent data
        has_conditions: session.user.healthProfile?.conditions?.length > 0,
        age_bracket: session.user.healthProfile?.age_bracket,
        activity_level: session.user.healthProfile?.activity_level,
      })
    } else if (status === 'unauthenticated') {
      posthog.reset()  // Clear identity on logout
    }
  }, [session, status])
}
```

Call this hook in your root dashboard layout so it fires once after login:

```typescript
// frontend/app/dashboard/layout.tsx
'use client'
import { usePostHogIdentify } from '@/hooks/usePostHogIdentify'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  usePostHogIdentify()
  return <>{children}</>
}
```

**5. Custom Event Tracking**

```typescript
// frontend/lib/analytics.ts
// Centralised event catalogue — import this everywhere, never call posthog directly

import { posthog } from './posthog'

export const analytics = {
  briefingGenerated(props: { aqi_value: number; aqi_category: string; city: string }) {
    posthog.capture('Briefing Generated', props)
  },

  briefingShared(props: { method: 'copy_link' | 'email' | 'whatsapp' }) {
    posthog.capture('Briefing Shared', props)
  },

  alertCreated(props: { threshold: number; pollutant: string }) {
    posthog.capture('Alert Created', props)
  },

  emailSubscribed(props: { frequency: 'daily' | 'twice_daily' }) {
    posthog.capture('Email Subscribed', props)
  },

  aiQuotaExhausted() {
    posthog.capture('AI Quota Exhausted')
  },

  fallbackBriefingShown(props: { aqi_value: number }) {
    posthog.capture('Fallback Briefing Shown', props)
  },

  locationAdded(props: { city: string; is_first_location: boolean }) {
    posthog.capture('Location Added', props)
  },

  onboardingCompleted(props: { has_conditions: boolean; activity_level: string }) {
    posthog.capture('Onboarding Completed', props)
  },
}
```

Usage example in a component:

```typescript
import { analytics } from '@/lib/analytics'

// After briefing API call resolves successfully:
analytics.briefingGenerated({
  aqi_value: briefing.aqi_value,
  aqi_category: briefing.category,
  city: userLocation.city,
})
```

**6. PostHog Feature Flags**

Use feature flags to safely roll out new features to a subset of users without a redeploy.

```typescript
// Check a feature flag before rendering new UI
import { useFeatureFlagEnabled } from 'posthog-js/react'

function NewAlertUI() {
  const isEnabled = useFeatureFlagEnabled('new-alert-threshold-ui')
  return isEnabled ? <NewAlertForm /> : <LegacyAlertForm />
}
```

Create flags in the PostHog dashboard under **Feature Flags → New flag**. Roll out to 10% of users first, monitor the `Alert Created` funnel, then expand to 100%.

**7. Key Funnels to Build in PostHog**

Configure these funnels under **Product Analytics → Funnels** in the PostHog dashboard:

| Funnel | Steps | Success Signal |
|---|---|---|
| Activation | Signed Up → Onboarding Completed → Briefing Generated | >50% complete within 24h |
| Email Retention | Briefing Generated → Email Subscribed | >40% |
| Briefing Engagement | Pageview (dashboard) → Briefing Generated → Session > 2min | >55% |
| Alert Setup | Pageview (dashboard) → Alert Created | >25% |

### Key Metrics to Monitor

| Metric | Target (Month 1) | PostHog Feature |
|---|---|---|
| Weekly Active Users | 100+ | Trends → Unique users |
| Activation rate (briefing within 24h of signup) | >50% | Funnels |
| Email subscription rate | >40% of registered users | Funnels |
| Session duration on dashboard | >2 min | Session recordings |
| AI quota exhaustion rate | <10% of sessions | Trends → `AI Quota Exhausted` |
| Onboarding completion rate | >80% | Funnels |

### Session Recordings

PostHog records anonymised session replays — useful for diagnosing UX friction. Enable in **Project Settings → Session Recording**. Free tier includes recordings. Recordings of authenticated users automatically link to their PostHog profile.

> **Privacy note:** PostHog masks all input fields by default. No password, health condition text, or personally typed data is captured in recordings. Verify this in your PostHog dashboard under **Session Recording → Data masking**.

### Vercel Analytics — Core Web Vitals

Vercel's built-in analytics tracks LCP, FID, and CLS with zero configuration on the hobby plan.

```bash
npm install @vercel/analytics @vercel/speed-insights
```

```typescript
// frontend/app/layout.tsx (additions)
import { Analytics } from '@vercel/analytics/react'
import { SpeedInsights } from '@vercel/speed-insights/next'

// Inside <body>, alongside PostHogProvider:
<Analytics />
<SpeedInsights />
```

Target Core Web Vitals thresholds for Google ranking eligibility:

| Metric | Good | Needs Improvement | Poor |
|---|---|---|---|
| LCP (Largest Contentful Paint) | ≤ 2.5s | 2.5–4s | > 4s |
| FID / INP (Interactivity) | ≤ 200ms | 200–500ms | > 500ms |
| CLS (Layout Shift) | ≤ 0.1 | 0.1–0.25 | > 0.25 |

---

## 21. Google SEO Protocols

### SEO Architecture Overview

This app has two distinct content surfaces that need separate SEO strategies:

**Surface A — Public marketing / city landing pages** (indexable, optimized for search)
**Surface B — Authenticated dashboard** (behind login, not indexed, excluded from crawlers)

All SEO work targets Surface A only.

### robots.txt

Place this at `frontend/public/robots.txt`. It blocks authenticated routes and allows everything else.

```
User-agent: *
Allow: /
Disallow: /dashboard/
Disallow: /api/
Disallow: /auth/

# Sitemap location
Sitemap: https://yourdomain.com/sitemap.xml
```

### Dynamic Sitemap

Generate the sitemap dynamically using Next.js App Router's built-in sitemap support. It auto-updates when new city pages are added.

```typescript
// frontend/app/sitemap.ts

import { MetadataRoute } from 'next'

// Add all cities that have landing pages
const TARGET_CITIES = [
  { slug: 'visakhapatnam', name: 'Visakhapatnam' },
  { slug: 'delhi',          name: 'Delhi' },
  { slug: 'mumbai',         name: 'Mumbai' },
  { slug: 'bangalore',      name: 'Bangalore' },
  { slug: 'hyderabad',      name: 'Hyderabad' },
  { slug: 'kolkata',        name: 'Kolkata' },
]

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://yourdomain.com'
  const now = new Date()

  const staticPages: MetadataRoute.Sitemap = [
    { url: baseUrl, lastModified: now, changeFrequency: 'daily', priority: 1.0 },
    { url: `${baseUrl}/about`, lastModified: now, changeFrequency: 'monthly', priority: 0.5 },
  ]

  const cityPages: MetadataRoute.Sitemap = TARGET_CITIES.map(city => ({
    url: `${baseUrl}/air-quality/${city.slug}`,
    lastModified: now,
    changeFrequency: 'hourly' as const,   // AQI data changes frequently
    priority: 0.9,
  }))

  return [...staticPages, ...cityPages]
}
```

### Metadata — Root Layout

Set global metadata defaults in `layout.tsx`. Every page inherits these and can override.

```typescript
// frontend/app/layout.tsx

import { Metadata } from 'next'

export const metadata: Metadata = {
  metadataBase: new URL('https://yourdomain.com'),
  title: {
    default: 'Air Quality Health Briefing — Know Your Air, Protect Your Health',
    template: '%s | Air Quality Briefing',
  },
  description:
    'Real-time air quality data fused with AI-generated health advice. ' +
    'Know if it is safe to exercise, what mask to wear, and what symptoms to watch — ' +
    'personalized to your health profile.',
  keywords: [
    'air quality', 'AQI', 'PM2.5', 'health briefing', 'air pollution India',
    'Visakhapatnam AQI', 'Delhi air quality', 'asthma outdoor safety',
  ],
  authors: [{ name: 'Air Quality Briefing' }],
  creator: 'Air Quality Briefing',
  openGraph: {
    type: 'website',
    locale: 'en_IN',
    url: 'https://yourdomain.com',
    siteName: 'Air Quality Health Briefing',
    title: 'Air Quality Health Briefing',
    description: 'AI-powered daily health advice based on your local air quality.',
    images: [{ url: '/og-default.png', width: 1200, height: 630, alt: 'Air Quality Briefing' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Air Quality Health Briefing',
    description: 'AI-powered daily health advice based on your local air quality.',
    images: ['/og-default.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, 'max-image-preview': 'large' },
  },
  alternates: { canonical: 'https://yourdomain.com' },
}
```

### City Landing Pages — Per-Page Metadata + Structured Data

Each city gets a dedicated page at `/air-quality/[city]`. These pages are the primary organic traffic targets.

```typescript
// frontend/app/air-quality/[city]/page.tsx

import { Metadata } from 'next'

interface Props {
  params: { city: string }
}

const CITY_META: Record<string, { name: string; state: string; lat: number; lon: number }> = {
  visakhapatnam: { name: 'Visakhapatnam', state: 'Andhra Pradesh', lat: 17.6868, lon: 83.2185 },
  delhi:         { name: 'Delhi',          state: 'Delhi',          lat: 28.7041, lon: 77.1025 },
  mumbai:        { name: 'Mumbai',         state: 'Maharashtra',    lat: 19.0760, lon: 72.8777 },
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const city = CITY_META[params.city]
  if (!city) return {}

  const title = `${city.name} Air Quality Today — AQI, PM2.5 & Health Advice`
  const description =
    `Live AQI for ${city.name}, ${city.state}. Real-time PM2.5, PM10, O3 levels ` +
    `with AI-generated health guidance for outdoor activity, masks, and symptom watch.`

  return {
    title,
    description,
    alternates: { canonical: `https://yourdomain.com/air-quality/${params.city}` },
    openGraph: {
      title,
      description,
      url: `https://yourdomain.com/air-quality/${params.city}`,
      images: [{ url: `/og-city-${params.city}.png`, width: 1200, height: 630 }],
    },
  }
}

// ── JSON-LD Structured Data ─────────────────────────────────────────────────
// Helps Google display rich results for air quality searches

function CityStructuredData({ city, aqiValue }: { city: typeof CITY_META[string]; aqiValue: number }) {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: `${city.name} Air Quality`,
    description: `Real-time AQI and health briefing for ${city.name}`,
    about: {
      '@type': 'Place',
      name: city.name,
      geo: {
        '@type': 'GeoCoordinates',
        latitude: city.lat,
        longitude: city.lon,
      },
    },
    // EnvironmentalObservation schema for AQI data
    mainEntity: {
      '@type': 'Observation',
      name: 'Air Quality Index',
      observationDate: new Date().toISOString(),
      measuredProperty: {
        '@type': 'Property',
        name: 'Air Quality Index (US EPA)',
      },
      measuredValue: aqiValue,
    },
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  )
}
```

### FAQPage Structured Data

Add an FAQ section to city pages to capture "People Also Ask" boxes in Google results.

```typescript
// Append to city page component

const FAQ_ITEMS = (cityName: string) => [
  {
    question: `What is the AQI in ${cityName} today?`,
    answer: `The current AQI in ${cityName} is updated every 15 minutes from the nearest OpenAQ monitoring station. Check the live gauge above for the latest reading.`,
  },
  {
    question: `Is it safe to exercise outdoors in ${cityName} today?`,
    answer: `Our AI health briefing evaluates the current AQI, PM2.5 levels, and your personal health profile to tell you whether outdoor exercise is safe, requires caution, or should be avoided.`,
  },
  {
    question: `What does AQI mean for my health?`,
    answer: `The Air Quality Index (AQI) runs from 0–500. 0–50 is Good (safe for all). 51–100 is Moderate. 101–150 is Unhealthy for Sensitive Groups. Above 150 is Unhealthy for everyone. Our briefing translates the number into specific actions.`,
  },
]

function FAQStructuredData({ cityName }: { cityName: string }) {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: FAQ_ITEMS(cityName).map(item => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: { '@type': 'Answer', text: item.answer },
    })),
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  )
}
```

### Google Search Console Setup

1. Go to [search.google.com/search-console](https://search.google.com/search-console)
2. Add property → choose **URL prefix** → enter `https://yourdomain.com`
3. Verify ownership via the **HTML tag method** — add the meta tag to `layout.tsx`:

```typescript
export const metadata: Metadata = {
  // ... existing metadata ...
  verification: {
    google: 'YOUR_GOOGLE_VERIFICATION_CODE',  // from Search Console
  },
}
```

4. After verification, submit your sitemap:
   - Go to **Sitemaps** → enter `sitemap.xml` → Submit

5. **Monitor weekly:**

| Report | What to Watch |
|---|---|
| Coverage | Ensure city pages are Indexed, not Excluded |
| Core Web Vitals | LCP < 2.5s; fix any Poor URLs before launching |
| Search Performance | Track impressions for "AQI [city]" queries |
| Rich Results | Verify FAQ and structured data are parsed correctly |

### On-Page SEO Checklist

Every city landing page must satisfy these before launch:

```
[ ] <title> contains target keyword + city name (under 60 chars)
[ ] <meta description> 120–155 chars, includes city + AQI + action word
[ ] H1 contains primary keyword (e.g., "Visakhapatnam Air Quality Today")
[ ] H2s cover secondary intent (health advice, pollutant breakdown, FAQ)
[ ] canonical URL set correctly — no trailing slash mismatch
[ ] JSON-LD structured data validated at search.google.com/test/rich-results
[ ] robots meta allows indexing (no accidental noindex in development)
[ ] Open Graph image is 1200×630px, no text too close to edges
[ ] Page loads in < 2.5s LCP on mobile (test with PageSpeed Insights)
[ ] Internal links from homepage → each city page (crawlability)
[ ] AQI data updates reflected in lastModified timestamp in sitemap.xml
```

### Nginx — SEO-Friendly Headers

Add these headers to your `nginx.conf` for crawlability and performance signals:

```nginx
# nginx/nginx.conf (additions to the server block)

server {
  # ... existing config ...

  # Canonical HTTPS redirect (avoids duplicate content)
  if ($scheme != "https") {
    return 301 https://$host$request_uri;
  }

  # Security + SEO headers
  add_header X-Robots-Tag "index, follow" always;
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
  add_header X-Content-Type-Options "nosniff" always;

  # Cache static assets aggressively (improves LCP score)
  location ~* \.(js|css|png|jpg|jpeg|webp|svg|ico|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
  }

  # Cache sitemap for 1 hour
  location = /sitemap.xml {
    expires 1h;
    add_header Cache-Control "public";
  }

  # robots.txt is static — cache it
  location = /robots.txt {
    expires 7d;
    add_header Cache-Control "public";
  }
}
```

### Target Keyword Strategy

Focus on **informational + local intent** queries. These have high click-through rates for health and environment tools.

| Primary Keyword | Monthly Volume (India) | Difficulty | Page Target |
|---|---|---|---|
| `visakhapatnam air quality today` | Medium | Low | `/air-quality/visakhapatnam` |
| `delhi AQI today` | High | Medium | `/air-quality/delhi` |
| `is it safe to run outside today [city]` | Low | Very Low | City pages + FAQ |
| `PM2.5 health effects asthma` | Medium | Low | Blog / about page |
| `air quality index meaning` | High | Medium | Homepage |
| `air pollution mask recommendation India` | Low | Low | City pages |

> **Programmatic SEO note:** The city landing page template scales to every city in OpenAQ's database with zero additional engineering. Each page auto-generates fresh AQI data, structured metadata, and FAQ content. A single template can cover 50+ Indian cities and rank for long-tail "air quality [city]" searches.

---

## Appendix: Quick Start

```bash
# Clone the repo
git clone https://github.com/yourname/air-quality-briefing.git
cd air-quality-briefing

# ── Get your free API keys ──────────────────────────────────
# OpenAQ:    https://explore.openaq.org  (sign up → get key)
# OpenRouter: https://openrouter.ai       (sign up → create key)
# Brevo:     https://brevo.com            (sign up → SMTP & API → key)
# Supabase:  https://supabase.com         (new project → settings → DB URL)
# Upstash:   https://console.upstash.com  (new DB → copy rediss:// URL)

# ── Backend setup ───────────────────────────────────────────
cd backend
cp .env.example .env
# Fill in the 5 values above + generate JWT secrets:
# python -c "import secrets; print(secrets.token_hex(32))"

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Celery worker (new terminal)
source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info

# ── Frontend setup ──────────────────────────────────────────
cd ../frontend
cp .env.local.example .env.local
# Fill in: NEXTAUTH_SECRET (random string), NEXTAUTH_URL

npm install
npm run dev

# App:      http://localhost:3000
# API docs: http://localhost:8000/docs

# ── Monitor your free tier limits ───────────────────────────
# Upstash:    console.upstash.com  → commands used today
# Brevo:      app.brevo.com        → emails sent today
# OpenRouter: openrouter.ai/activity → AI requests today
# Supabase:   supabase.com/dashboard → DB size and connections

# ── Analytics & SEO setup (post-deploy) ─────────────────────
# 1. PostHog Cloud setup (see Section 20)
#    → Sign up at posthog.com (free, no card)
#    → Create project → copy Project API Key (phc_...)
#    → Add to .env.local: NEXT_PUBLIC_POSTHOG_KEY and NEXT_PUBLIC_POSTHOG_HOST
#    → npm install posthog-js
# 2. Submit sitemap to Google Search Console:
#    → https://search.google.com/search-console
#    → Add property → verify → submit https://yourdomain.com/sitemap.xml
# 3. Validate structured data:
#    → https://search.google.com/test/rich-results
#    → Test a city page URL (e.g. /air-quality/visakhapatnam)
# 4. Check Core Web Vitals:
#    → https://pagespeed.web.dev → enter your deployed URL → target LCP < 2.5s
# 5. Monitor PostHog:
#    → posthog.com/dashboard → check Activation funnel daily for first 2 weeks
```

---

*This document is the single source of truth for architecture, security, and implementation decisions. Every service listed is free. Update this document with every significant architectural change.*
